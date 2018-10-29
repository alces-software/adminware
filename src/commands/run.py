
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
    def batch(ctx, **kwargs):
        set_nodes_context(ctx, **kwargs)

    @click_tools.command(batch, exclude_interactive_only = True)
    @click.pass_context
    def runnner(ctx, config, arguments):
        nodes = ctx.obj['adminware']['nodes']
        if not nodes:
            raise ClickException('Please give either --node or --group')
        batch = [Batch(config = config.path, arguments = arguments)]
        execute_batch(batch, nodes)

    def execute_batch(batches, nodes):
        class JobRunner:
            def __init__(self, node, batch):
                self.node = node
                self.batch = batch
                self.thread = threading.Thread(target=self.run)

            def run(self):
                local_session = Session()
                try:
                    local_batch = local_session.merge(self.batch)
                    job = Job(node = self.node, batch = local_batch)
                    local_session.add(job)
                    job.run()
                    if job.exit_code == 0:
                        symbol = 'Pass'
                    else:
                        symbol = 'Failed: {}'.format(job.exit_code)
                    click.echo('{}: {}'.format(job.node, symbol))
                finally:
                    local_session.commit()
                    Session.remove()

        session = Session()
        try:
            for batch in batches:
                session.add(batch)
                session.commit()
                click.echo('Batch: {}\nExecuting: {}'.format(batch.id, batch.__name__()))
                threads = list(map(lambda n: JobRunner(n, batch).thread, nodes))
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
