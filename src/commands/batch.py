
import click
from click import ClickException
from action import ClickGlob
import groups
from terminaltables import AsciiTable

from cli_utils import set_nodes_context
from database import Session

from models.job import Job
from models.batch import Batch

def add_commands(appliance):

    @appliance.group(help='Manage running a command over the nodes')
    def batch():
        pass

    @batch.command(help='Retrieves the batch result summaries')
    @click.option('--node', '-n', metavar='NODE',
                  help='Retrieve the previous result for a node')
    @click.option('--group', '-g', metavar='GROUP',
                  help='Retrieve the results for all nodes in group')
    @click.option('--batch-id', '-i', metavar='ID', type=int,
                  help='Retrieve results for a particular batch')
    @click.pass_context
    def history(ctx, **options):
        set_nodes_context(ctx, **options)
        nodes = ctx.obj['adminware']['nodes']
        batch_id = options['batch_id']
        session = Session()
        query = session.query(Job)
        if not (nodes or batch_id):
            raise ClickException('Please specify a filter')
        if nodes: query = query.filter(Job.node.in_(nodes))
        if batch_id:
            query = query.join(Job, Batch.jobs) \
                         .filter(Batch.id == int(batch_id))
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

    @batch.command(help='List the recently ran batches')
    @click.option('--limit', '-l', default=10, type=int, metavar='NUM',
                  help='Return the last NUM of batches')
    def list(limit):
        session = Session()
        try:
            query = session.query(Batch) \
                           .order_by(Batch.created_date.desc()) \
                           .limit(limit)
            rows = [['ID', 'Date', 'Name', 'Nodes']]
            for batch in query.all():
                nodes = [job.node for job in batch.jobs]
                nodes_str = ','.join(nodes)
                row = [
                    batch.id, batch.created_date, batch.__name__(),
                    nodes_str
                ]
                rows.append(row)
            print(AsciiTable(rows).table)

        finally:
            session.close()

    @batch.command(help='Inspect a previous batch')
    @click.argument('batch_id', type=int)
    @click.argument('node')
    def view(batch_id, node):
        session = Session()
        job = session.query(Job) \
                     .filter(Job.node == node) \
                     .join(Job, Batch.jobs) \
                     .filter(Batch.id == int(batch_id)) \
                     .first()
        if job == None: raise ClickException('No job found')
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

    @batch.group(help='Run a command on a node or group')
    @click.option('--node', '-n', metavar='NODE',
                  help='Runs the command on the node')
    @click.option('--group', '-g', metavar='GROUP',
                  help='Runs the command over the group')
    @click.pass_context
    def run(ctx, **kwargs):
        set_nodes_context(ctx, **kwargs)

    @ClickGlob.command(run, 'batch')
    @click.pass_context
    def run_batch(ctx, config, arguments):
        nodes = ctx.obj['adminware']['nodes']
        if not nodes:
            raise ClickException('Please give either --node or --group')
        batch = Batch(config = config.path, arguments = arguments)
        session = Session()
        try:
            session.add(batch)
            session.commit() # Saves the batch to receive and id
            print("Batch: {}".format(batch.id))
            for node in nodes:
                job = Job(node = node, batch = batch)
                session.add(job)
                job.run()
                if job.exit_code == 0:
                    symbol = 'Pass'
                else:
                    symbol = 'Failed: {}'.format(job.exit_code)
                print("{}: {}".format(job.node, symbol))
        finally:
            session.commit()
            session.close()
