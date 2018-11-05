
import click
from click import ClickException
import cli_utils

from database import Session
from models.job import Job
from models.batch import Batch
from models.config import Config

import threading

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
                    batch.jobs[0].run()
                finally:
                    session.commit()
                    Session.remove()
            elif batch.jobs:
                raise ClickException('''
'{}' is an interactive command and can only be ran on a single node
'''.strip())
            else:
                raise ClickException('Please specify a node with --node')
        elif batch.jobs:
            execute_threaded_batches([batch])
        else:
            raise ClickException('Please give either --node or --group')

    @run.group(help='Run a family of commands on node(s) or group(s)')
    def family(): pass

    family_runner = {
        'help': 'Runs the command over the group',
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
            #create batch w/ relevant config for command
            batch = Batch(config = config.path)
            batch.build_jobs(*nodes)
            batches += [batch]
        execute_threaded_batches(batches)

    def execute_threaded_batches(batches):
        runners = []
        active_runners = []

        class JobRunner:
            def __init__(self, job):
                self.unsafe_job = job # This Job object may not thread safe
                self.thread = threading.Thread(target=self.run)
                self.job = None

            def run(self):
                local_session = Session()
                try:
                    job = self.job = local_session.merge(self.unsafe_job)
                    job.run()
                    if job.exit_code == 0:
                        symbol = 'Pass'
                    else:
                        symbol = 'Failed: {}'.format(job.exit_code)
                    click.echo('ID: {}, Node: {}, {}'.format(job.id, job.node, symbol))
                finally:
                    local_session.commit()
                    Session.remove()

        session = Session()
        try:
            for batch in batches:
                session.add(batch)
                session.commit()
                click.echo('Executing: {}'.format(batch.__name__()))
                runners += list(map(lambda j: JobRunner(j), batch.jobs))
                runners.reverse()
                while len(runners) > 0 or len(active_runners) > 0:
                    while len(active_runners) < 10 and len(runners) > 0:
                        new_run = runners.pop()
                        new_run.thread.start()
                        active_runners.append(new_run)
                    for run in active_runners:
                        if not run.thread.is_alive():
                            run.thread.join()
                            active_runners.remove(run)
        finally:
            session.commit()
            Session.remove()
