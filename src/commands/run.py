
import click
from click import ClickException
import click_tools
from cli_utils import set_nodes_context

from database import Session
from models.job import Job
from models.batch import Batch

import threading

def add_commands(appliance):
    @appliance.group(help='Run a tool within your cluster')
    def run():
        pass

    @run.group(help='Run a tool over a batch of nodes')
    @click.option('--node', '-n', multiple=True, metavar='NODE',
                  help='Runs the command on the node')
    @click.option('--group', '-g', multiple=True, metavar='GROUP',
                  help='Runs the command over the group')
    @click.pass_context
    def tool(ctx, **kwargs):
        set_nodes_context(ctx, **kwargs)

    @click_tools.command(tool)
    @click.pass_context
    def runnner(ctx, config, arguments):
        nodes = ctx.obj['adminware']['nodes']
        batch = Batch(config = config.path, arguments = arguments)
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
    @click.option('--node', '-n', multiple=True, metavar='NODE',
              help='Runs the command on the node')
    @click.option('--group', '-g', multiple=True, metavar='GROUP',
              help='Runs the command over the group')
    @click.pass_context
    def family(ctx, **kwargs):
        set_nodes_context(ctx, **kwargs)

    @click_tools.command_family(family)
    @click.pass_context
    def family_runner(ctx, family, command_configs):
        nodes = ctx.obj['adminware']['nodes']
        if not nodes:
            raise ClickException('Please give either --node or --group')
        batches = []
        for config in command_configs:
            #create batch w/ relevant config for command
            batch = Batch(config = config.path)
            batch.build_jobs(*nodes)
            batches += [batch]
        execute_threaded_batches(batches)

    def execute_threaded_batches(batches):
        class JobRunner:
            def __init__(self, job):
                self.unsafe_job = job # This Job object may not thread safe
                self.thread = threading.Thread(target=self.run)

            def run(self):
                local_session = Session()
                try:
                    job = local_session.merge(self.unsafe_job)
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
                jobs = list(map(lambda n: Job(node = n, batch = batch), nodes))
                session.add(batch)
                session.commit()
                click.echo('Executing: {}'.format(batch.__name__()))
                threads = list(map(lambda j: JobRunner(j).thread, batch.jobs))
                threads.reverse()
                active_threads = []
                while len(threads) > 0 or len(active_threads) > 0:
                    while len(active_threads) < 10 and len(threads) > 0:
                        new_thread = threads.pop()
                        new_thread.start()
                        active_threads.append(new_thread)
                    for thread in active_threads:
                        if not thread.is_alive():
                            active_threads.remove(thread)
        finally:
            session.commit()
            Session.remove()
