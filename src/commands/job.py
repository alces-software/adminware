
import click
import threading

from click import ClickException
from os.path import basename, join
from database import Session
from sqlalchemy import func

import explore_tools
import click_tools

from models.job import Job
from models.batch import Batch
from cli_utils import set_nodes_context
from appliance_cli.text import display_table

def add_commands(appliance):
    @appliance.group(help='Run, view, and inspect jobs')
    def job():
        pass

    @job.command(name='node-log', help="View the history of execution on a node")
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
                   'No. Runs']

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

    @job.command(help='Retrieves recently ran jobs')
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

    @job.command(help="Retrieves jobs' result summaries")
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

