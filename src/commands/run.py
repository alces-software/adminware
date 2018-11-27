
import click
from click import ClickException
import cli_utils

from database import Session
from models.job import Job
from models.batch import Batch
from models.config import Config
import command_creator
import groups as groups_util

import asyncio
import concurrent
import signal

import os

def add_commands(appliance):
    @appliance.group(help='Run a tool within your cluster')
    def run():
        pass

    run_options = {
        'options': {
            **cli_utils.hash__node__group,
            ('--yes', '-y'): {
                'help': 'Skip the confirmation prompt',
                'is_flag': True
            }
        }
    }

    runner_cmd = {
        'help': Config.help,
        **run_options,
        'arguments': Config.args
    }
    runner_group = {
        'help': (lambda names: "Run tools in {}".format(' '.join(names))),
        'invoke_without_command': True,
        **run_options
    }

    @command_creator.tools(run, command = runner_cmd, group = runner_group)
    @cli_utils.with__node__group
    @cli_utils.ignore_parent_commands
    def runner(_ctx, configs, argv, options, nodes):
        def error_if_invalid_interactive_batch():
            matches = [c for c in configs if c.interactive()]
            if matches and (len(configs) > 1 or len(nodes) > 1):
                if len(configs) > 1:
                    suffix = 'cannot be ran as part of a tool group'
                else:
                    suffix = 'can only be ran on a single node'
                raise ClickException('''
'{}' is an interactive tool and {}
'''.strip().format(matches[0].name(), suffix))

        def error_if_no_nodes():
            if not nodes:
                raise ClickException('Please give either --node or --group')

        def is_quiet():
            if len(configs) > 1: return False
            first = configs[0]
            if first.interactive() or first.report: return True
            else: return False

        def argument_hash(config):
            keys = config.args()
            arg_hash = {}
            for index, value in enumerate(argv):
                arg_hash[keys[index]] = value
            return arg_hash

        def build_batches():
            def build(config):
                batch = Batch(config = config.path)
                batch.build_jobs(*nodes)
                batch.build_shell_variables(**argument_hash(config))
                return batch
            return list(map(lambda c: build(c), configs))

        def get_confirmation(batches, nodes):
            tool_names = '\n  '.join([b.config_model.name() for b in batches])
            node_names = groups_util.compress_nodes(nodes).replace('],', ']\n  ')
            node_tag = 'node' if len(nodes) == 1 else 'nodes'
            click.echo("""
You are about to run:
  {}
Over {}:
  {}
""".strip().format(tool_names, node_tag, node_names))
            question = "Please enter [y/n] to confirm"
            affirmatives = ['y', 'ye', 'yes']
            reply = click.prompt(question).lower()
            if reply in affirmatives: return True

        error_if_no_nodes()
        error_if_invalid_interactive_batch()

        batches = build_batches()

        if (options['yes'].value or get_confirmation(batches, nodes)):
            execute_batches(batches, quiet = is_quiet())

    def execute_batches(batches, quiet = False):
        def run_print(string):
            if quiet: return
            click.echo(string)

        loop = asyncio.get_event_loop()
        def handler_interrupt():
            run_print('Interrupt Received! ')
            run_print('Cancelling the jobs...')
            for task in asyncio.Task.all_tasks(loop = loop):
                task.cancel()
        loop.add_signal_handler(signal.SIGINT, handler_interrupt)

        max_ssh = int(os.environ.setdefault('ADMINWARE_MAX_SSH', '100'))
        start_delay = float(os.environ.setdefault('ADMINWARE_START_DELAY', '0.2'))
        pool = concurrent.futures.ThreadPoolExecutor(max_workers = max_ssh)

        async def start_tasks(tasks):
            active_tasks = []
            def remove_done_tasks():
                for active_task in active_tasks:
                    if active_task.finished():
                        active_tasks.remove(active_task)
                        break

            async def add_tasks():
                for task in tasks:
                    while len(active_tasks) > max_ssh:
                        remove_done_tasks()
                        await asyncio.sleep(0.01)
                    asyncio.ensure_future(task, loop = loop)
                    active_tasks.append(task)
                    run_print('Starting Job: {}'.format(task.node))
                    await(asyncio.sleep(start_delay))

            async def await_finished():
                while len(active_tasks) > 0:
                    remove_done_tasks()
                    await asyncio.sleep(0.01)

            try:
                await add_tasks()
                run_print('Waiting for jobs to finish...')
            finally: await await_finished()

        session = Session()
        try:
            for batch in batches:
                session.add(batch)
                session.commit()
                # Ensure the models are loaded from the db
                batch.jobs
                batch.shell_variables
                run_print('Executing: {}'.format(batch.name()))
                tasks = map(lambda j: j.task(thread_pool = pool), batch.jobs)
                loop.run_until_complete(start_tasks(tasks))
        except concurrent.futures.CancelledError: pass
        finally:
            run_print('Cleaning up...')
            pool.shutdown(wait = True)
            run_print('Saving...')
            session.commit()
            Session.remove()
            run_print('Done')
