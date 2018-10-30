
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

    @run.group(help='Run a tool in an interactive shell')
    @click.option('--node', '-n', help='The node to run on')
    @click.pass_context
    def interactive(ctx, **kwargs):
        if not 'node' in kwargs or not kwargs['node']:
            raise ClickException("Please specify a node")
        ctx.obj = { 'adminware' : { 'node' : kwargs['node'] } }

    @click_tools.command(interactive)
    @click.pass_context
    def interactive_runner(ctx, config, arguments):
        batch = Batch(config = config.path, arguments = arguments)
        job = Job(node = ctx.obj['adminware']['node'], batch = batch)
        job.run(interactive = True)
        # Display the error if adminware errors (e.g. failed ssh connection)
        if job.exit_code < 0: raise ClickException(job.stderr)

    @run.group(help='Run a tool over a batch of nodes')
    @click.option('--node', '-n', multiple=True, metavar='NODE',
                  help='Runs the command on the node')
    @click.option('--group', '-g', multiple=True, metavar='GROUP',
                  help='Runs the command over the group')
    @click.pass_context
    def tool(ctx, **kwargs):
        set_nodes_context(ctx, **kwargs)

    @click_tools.command(tool, exclude_interactive_only = True)
    @click.pass_context
    def runnner(ctx, config, arguments):
        nodes = ctx.obj['adminware']['nodes']
        if not nodes:
            raise ClickException('Please give either --node or --group')
        batch = [Batch(config = config.path, arguments = arguments)]
        execute_batches(batch, nodes)

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
            batches += [Batch(config=config.path)]
        execute_batches(batches, nodes)

    def execute_batches(batches, nodes):
        class JobRunner:
            def __init__(self, job):
                self.unsafe_job = job # This Job object may not thread safe
                self.thread = threading.Thread(target=self.run)

            def run(self):
                local_session = Session()
                try:
                    job = local_session.merge(self.unsafe_job)
                    job.run()
                    local_session.commit()
                    if job.exit_code == 0:
                        symbol = 'Pass'
                    else:
                        symbol = 'Failed: {}'.format(job.exit_code)
                    click.echo('ID: {}, Node: {}, {}'.format(job.id, job.node, symbol))
                except:
                    local_session.commit()
                finally:
                    Session.remove()

        session = Session()
        try:
            for batch in batches:
                session.add(batch)
                session.commit()
                click.echo('Executing: {}'.format(batch.__name__()))
                jobs = list(map(lambda n: Job(node = n, batch = batch), nodes))
                threads = list(map(lambda j: JobRunner(j).thread, jobs))
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
