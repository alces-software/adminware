
import click
from click import ClickException
import cli_utils

from database import Session
from models.job import Job
from models.batch import Batch
from models.config import Config

import asyncio
import concurrent
import signal

import os

def add_commands(appliance):
    @appliance.group(help='Run a tool within your cluster')
    def run():
        pass

    @run.group(help='Run a tool over a batch of nodes')
    def tool():
        pass

    node_group_options = {
        ('--node', '-n'): {
            'help': 'Specify a node, repeat the flag for multiple',
            'multiple': True,
            'metavar': 'NODE'
        },
        ('--group', '-g'): {
            'help': 'Specify a group, repeat the flag for multiple',
            'multiple': True,
            'metavar': 'GROUP'
        }
    }

    runner_cmd = {
        'help': Config.help,
        'arguments': [['remote_arguments']], # [[]]: Optional Arg
        'options': node_group_options
    }
    runner_group = {
        'help': (lambda names: "Run further tools: '{}'".format(' '.join(names)))
    }

    @Config.commands(tool, command = runner_cmd, group = runner_group)
    @cli_utils.with__node__group
    def runner(config, argv, _, nodes):
        batch = Batch(config = config.path, arguments = (argv[0] or ''))
        batch.build_jobs(*nodes)
        if batch.is_interactive():
            if len(batch.jobs) == 1:
                session = Session()
                try:
                    session.add(batch)
                    session.add(batch.jobs[0])
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(batch.jobs[0].task())
                finally:
                    session.commit()
                    Session.remove()
            elif batch.jobs:
                raise ClickException('''
'{}' is an interactive tool and can only be ran on a single node
'''.format(config.name()).strip())
            else:
                raise ClickException('Please specify a node with --node')
        elif batch.jobs:
            execute_threaded_batches([batch])
        else:
            raise ClickException('Please give either --node or --group')

    @run.group(help='Run a family of tools on node(s) or group(s)')
    def family(): pass

    family_runner = {
        'help': 'Runs the tool over the group',
        'options': node_group_options
    }

    @Config.family_commands(family, command = family_runner)
    @cli_utils.with__node__group
    def family_runner(callstack, _a, _o, nodes):
        family = callstack[0]
        if not nodes:
            raise ClickException('Please give either --node or --group')
        batches = []
        for config in Config.all_families()[family]:
            #create batch w/ relevant config for tool
            batch = Batch(config = config.path)
            batch.build_jobs(*nodes)
            batches += [batch]
        execute_threaded_batches(batches)

    def execute_threaded_batches(batches):
        loop = asyncio.get_event_loop()
        def handler_interrupt():
            print('Interrupt Received! ')
            print('Cancelling the jobs...')
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
                print('Starting Job: {}'.format(task.node))
                await(asyncio.sleep(start_delay))
            print('Waiting for jobs to finish...')
            while len(active_tasks) > 0:
                remove_done_tasks()
                await asyncio.sleep(0.01)

        session = Session()
        try:
            for batch in batches:
                session.add(batch)
                session.commit()
                click.echo('Executing: {}'.format(batch.__name__()))
                tasks = map(lambda j: j.task(thread_pool = pool), batch.jobs)
                loop.run_until_complete(start_tasks(tasks))
        except concurrent.futures.CancelledError: pass
        finally:
            print('Cleaning up...')
            pool.shutdown(wait = True)
            print('Saving...')
            session.commit()
            Session.remove()
            print('Done')
