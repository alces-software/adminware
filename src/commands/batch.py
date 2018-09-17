
import click
import action
import groups
from terminaltables import AsciiTable

from cli_utils import set_nodes_context
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
    @click.pass_context
    def history(ctx, **options):
        set_nodes_context(ctx, **options)
        session = Session()
        batches = session.query(Batch).all()
        def table_rows():
            rows = [['Batch', 'Command', 'Date']]
            for batch in batches:
                row = [batch.id, batch.__name__(), batch.created_date]
                rows.append(row)
            return rows
        print(AsciiTable(table_rows()).table)

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
        set_nodes_context(ctx, **kwargs)
    action.add_actions(run, 'batch')

