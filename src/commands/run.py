
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
    def runner(_ctx, configs, _a, options, nodes):
        def error_if_invalid_interactive_batch():
            matches = [b for b in batches if b.is_interactive()]
            if matches and (len(batches) > 1 or len(nodes) > 1):
                if len(batches) > 1:
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
            if len(batches) > 1: return False
            first = batches[0]
            if first.is_interactive or first.report: return True
            else: return False

        error_if_no_nodes()
        batches = list(map(lambda c: Batch(config = c.path), configs))
        error_if_invalid_interactive_batch()
        if not (options['yes'].value or get_confirmation(batches, nodes)):
            return
        for batch in batches: batch.build_jobs(*nodes)
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
        if reply in affirmatives:
            return True
