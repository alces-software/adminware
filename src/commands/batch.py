
import click
import action
import groups

from database import Session
from models.batch import Batch

def add_commands(appliance):

    @appliance.group(help='TODO')
    def batch():
        pass

    @batch.command(help='TODO')
    @click.option('--node', '-n')
    @click.option('--group', '-g')
    @click.option('--job-id', '-j')
    def history(**options):
        session = Session()
        print(session.query(Batch).all())

    @batch.command(help='TODO')
    @click.argument('job_id')
    @click.argument('node')
    def view(job_id, node):
        pass

    @batch.group(help='TODO')
    @click.option('--node', '-n')
    @click.option('--group', '-g')
    @click.pass_context
    def run(ctx, **kwargs):
        obj = { 'nodes' : [] }
        if kwargs['node']: obj['nodes'].append(kwargs['node'])
        if kwargs['group']:
            obj['nodes'].extend(groups.nodes_in(kwargs['group']))
        ctx.obj = { 'adminware' : obj }
        pass
    action.add_actions(run, 'batch')

