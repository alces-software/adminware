
import click
import action
import groups
from terminaltables import AsciiTable

from cli_utils import set_nodes_context
from database import Session

from models.job import Job
from models.batch import Batch

def add_commands(appliance):

    @appliance.group(help='TODO')
    def batch():
        pass

    @batch.command(help='TODO')
    @click.option('--node', '-n')
    @click.option('--group', '-g')
    @click.option('--batch-id', '-i')
    @click.pass_context
    def history(ctx, **options):
        set_nodes_context(ctx, **options)
        nodes = ctx.obj['adminware']['nodes']
        batch_id_filter = options['batch_id']
        session = Session()
        query = session.query(Job) \
                       .filter(Job.node.in_(nodes))
        if options['batch_id']:
            query = query.join(Job, Batch.jobs) \
                         .filter(Batch.id == int(options['batch_id']))
        jobs = query.all()
        jobs = sorted(jobs, key=lambda job: job.created_date, reverse=True)
        def table_rows():
            rows = [['Batch', 'Node', 'Command', 'Exit Code', 'Date']]
            for job in jobs:
                batch = job.batch
                row = [batch.id,
                       job.node,
                       batch.__name__(),
                       job.exit_code,
                       batch.created_date]
                rows.append(row)
            return rows
        print(AsciiTable(table_rows()).table)

    @batch.command(help='TODO')
    @click.argument('batch_id')
    @click.argument('node')
    def view(batch_id, node):
        session = Session()
        job = session.query(Job) \
                     .filter(Job.node == node) \
                     .join(Job, Batch.jobs) \
                     .filter(Batch.id == int(batch_id)) \
                     .first()
        if job == None:
            click.echo('No job found', err=True)
            exit(1)
        table_data = [
            ['Date', job.created_date],
            ['Batch', job.batch.id],
            ['Node', job.node],
            ['Command', job.batch.__name__()],
            ['Exit Code', job.exit_code],
            ['STDOUT', job.stdout],
            ['STDERR', job.stderr]
        ]
        table = AsciiTable(table_data)
        table.inner_row_border = True
        print(table.table)

    @batch.group(help='TODO')
    @click.option('--node', '-n')
    @click.option('--group', '-g')
    @click.pass_context
    def run(ctx, **kwargs):
        set_nodes_context(ctx, **kwargs)
    action.add_actions(run, 'batch')

