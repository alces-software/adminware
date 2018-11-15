
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
        'arguments': [['remote_arguments']], # [[]]: Optional Arg
        **run_options
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
        if not (options['yes'].value or get_confirmation(configs, nodes)):
            return
        if not argv: argv = [None]
        if len(configs) > 1:
            for config in configs:
                if config.interactive():
                    raise ClickException('''
'{}' is an interactive tool and cannot be ran as part of a group
'''.format(config.__name__()).strip())
        for config in configs:
            batch = Batch(config = config.path, arguments = (argv[0] or ''))
            batch.build_jobs(*nodes)
            if batch.is_interactive():
                if len(batch.jobs) == 1:
                    execute_threaded_batches([batch], quiet = True)
                elif batch.jobs:
                    raise ClickException('''
'{}' is an interactive tool and can only be ran on a single node
'''.format(config.name()).strip())
                else:
                    raise ClickException('Please specify a node with --node')
            elif batch.jobs:
                report = batch.config_model.report
                execute_threaded_batches([batch], quiet = report)
            else:
                raise ClickException('Please give either --node or --group')

    def execute_threaded_batches(batches, quiet = False):
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
                    if active_task._state == 'FINISHED':
                        active_tasks.remove(active_task)
                        break
            for task in tasks:
                while len(active_tasks) > max_ssh:
                    remove_done_tasks()
                    await asyncio.sleep(0.01)
                asyncio.ensure_future(task, loop = loop)
                active_tasks.append(task)
                run_print('Starting Job: {}'.format(task.node))
                await(asyncio.sleep(start_delay))
            run_print('Waiting for jobs to finish...')
            while len(active_tasks) > 0:
                remove_done_tasks()
                await asyncio.sleep(0.01)

        session = Session()
        try:
            for batch in batches:
                session.add(batch)
                session.commit()
                run_print('Executing: {}'.format(batch.__name__()))
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

    def get_confirmation(configs, nodes):
        tool_names = '\n'.join([c.name() for c in configs])
        node_names = groups_util.compress_nodes(nodes)[0].replace(',', ', ')
        click.echo("""
You are about to run:
{}
Over nodes: {}
""".strip().format(tool_names, node_names))
        question = "Please enter [y/n] to confirm"
        affirmatives = ['y', 'ye', 'yes']
        negatives = ['n', 'no']
        while "answer is invalid":
            reply = click.prompt(question).lower()
            if reply in affirmatives:
                return True
            if reply in negatives:
                return False
