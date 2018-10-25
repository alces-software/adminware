
import click
from click import ClickException
from action import ClickGlob
import groups

from cli_utils import set_nodes_context
from database import Session
from sqlalchemy import func

from models.job import Job
from models.batch import Batch
from appliance_cli.text import display_table

def add_commands(appliance):

    @appliance.group(help='Manage running a command over the nodes')
    def batch():
        pass

    @batch.command(help="Retrieves batches' result summaries")
    @click.option('--node', '-n', multiple=True, metavar='NODE',
                  help='Retrieve the previous result for a node')
    @click.option('--group', '-g', multiple=True, metavar='GROUP',
                  help='Retrieve the results for all nodes in group')
    @click.option('--batch-id', '-i', metavar='ID', type=int,
                  help='Retrieve results for a particular batch')
    @click.pass_context
    def filter(ctx, **options):
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
        headers = ['ID', 'Node', 'Exit Code', 'Command', 'Date']
        def table_rows():
            rows = []
            for job in jobs:
                batch = job.batch
                row = [batch.id,
                       job.node,
                       job.exit_code,
                       batch.__name__(),
                       batch.created_date]
                rows.append(row)
            return rows
        display_table(headers, table_rows())

    @batch.command(help='Retrieves the recently ran batches')
    @click.option('--limit', '-l', default=10, type=int, metavar='NUM',
                  help='Return the last NUM batches')
    def history(limit):
        session = Session()
        try:
            query = session.query(Batch) \
                           .order_by(Batch.created_date.desc()) \
                           .limit(limit)
            headers = ['ID', 'Nodes', 'Command', 'Arguments', 'Date']
            rows = []

            for batch in query.all():
                nodes = [job.node for job in batch.jobs]
                nodes_str = ','.join(nodes)
                row = [
                    batch.id, nodes_str, batch.__name__(),
                    batch.arguments, batch.created_date
                ]
                rows.append(row)
            display_table(headers, rows)

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
            ['Batch ID', job.batch.id],
            ['Node', job.node],
            ['Exit Code', job.exit_code],
            ['Command', job.batch.__name__()],
            ['Arguments', job.batch.arguments],
            ['STDOUT', job.stdout],
            ['STDERR', job.stderr]
        ]
        display_table([], table_data)

    @batch.command(name='node-log',help="View the execution of each command on a node")
    @click.argument('node', type=str)
    # note: this works on config location, not command name.
    # Any commands that are moved will be considered distinct.
    def node_log(node):
        session = Session()
        # returns 2-length tuples of the Job data and the amount of times the command's been run on <node>
        job_query = session.query(Job, func.count(Batch.config))\
                           .filter(Job.node == node)\
                           .join("batch")\
                           .order_by(Job.created_date.desc())\
                           .group_by(Batch.config)\
                           .all()
        if not job_query: raise ClickException('No jobs found for node {}'.format(node))
        headers = ['Command',
                   'Exit Code',
                   'Batch',
                   'Arguments',
                   'Date',
                   'No. Reruns']

        rows = []
        for command in job_query:
            count = command[1]
            command = command[0]
            arguments = None if not command.batch.arguments else command.batch.arguments
            row = [command.batch.__name__(),
                   command.exit_code,
                   command.batch.id,
                   arguments,
                   command.created_date,
                   count]
            rows += [row]
            # sort by command name
            rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    @batch.group(help='Run a command on node(s) or group(s)')
    @click.option('--node', '-n', multiple=True, metavar='NODE',
                  help='Runs the command on the node')
    @click.option('--group', '-g', multiple=True, metavar='GROUP',
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
        batch = [Batch(config = config.path, arguments = arguments)]
        execute_batch(batch, nodes)

    @batch.group(name='run-family', help='Run a family of commands on node(s) or group(s)')
    @click.option('--node', '-n', multiple=True, metavar='NODE',
              help='Runs the command on the node')
    @click.option('--group', '-g', multiple=True, metavar='GROUP',
              help='Runs the command over the group')
    @click.pass_context
    def run_family(ctx, **kwargs):
        set_nodes_context(ctx, **kwargs)

    @ClickGlob.command_family(run_family, 'batch')
    @click.pass_context
    def run_batch_family(ctx, family, command_configs):
        nodes = ctx.obj['adminware']['nodes']
        if not nodes:
            raise ClickException('Please give either --node or --group')
        batches = []
        for config in command_configs:
            #create batch w/ relevant config for command
            batches += [Batch(config=config.path)]
        execute_batch(batches, nodes)

    def execute_batch(batches, nodes):
        session = Session()
        output = ''
        try:
            for batch in batches:
                if output: output = output + '\n'
                session.add(batch)
                session.commit()
                output = output + 'Batch: {}\nExecuting: {}'.format(batch.id, batch.__name__())
                for node in nodes:
                    job = Job(node = node, batch = batch)
                    session.add(job)
                    job.run()
                    if job.exit_code == 0:
                        symbol = 'Pass'
                    else:
                        symbol = 'Failed: {}'.format(job.exit_code)
                    output = output + '\n{}: {}'.format(job.node, symbol)
        finally:
            session.commit()
            session.close()
            click.echo_via_pager(output)

