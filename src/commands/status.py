
from appliance_cli.text import display_table
import click

from database import Session
from models.batch import Batch
from models.job import Job
from models.config import Config

import groups

import sqlalchemy

def add_commands(appliance):
    @appliance.command(help='FIX ME')
    @click.option('--node', '-n', multiple=True, metavar='NODE',
                  help='Retrieve the previous result for a node')
    @click.option('--group', '-g', multiple=True, metavar='GROUP',
                  help='Retrieve the results for all nodes in group')
    def status(node = [], group = []):
        nodes = list(node)
        for g in group: nodes += list(groups.nodes_in(g))
        node = nodes[0]
        session = Session()
        # Returns the most recent job for each tool and number of times it's been ran
        # Refs: https://docs.sqlalchemy.org/en/latest/core/functions.html#sqlalchemy.sql.functions.count
        #       https://www.w3schools.com/sql/func_sqlserver_count.asp
        # => [(latest_job1, count1), (lastest_job2, count2), ...]
        job_data = session.query(Job, sqlalchemy.func.count(Batch.config))\
                           .filter(Job.node.in_(nodes))\
                           .join("batch")\
                           .order_by(Job.created_date.desc())\
                           .group_by(Job.node, Batch.config)\
                           .all()
        if not job_data: raise click.ClickException('No jobs found for node {}'.format(node))
        job_objects = [i for i, j in job_data]
        headers, rows = shared_job_data_table(job_objects)
        headers = headers + ['No. Runs']
        for i, (job, count) in enumerate(job_data):
            rows[i] = rows[i] + [count]
        # sort by first column
        rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    def shared_job_data_table(data):
        headers = ['Job ID',
                   'Tool',
                   'Exit Code',
                   'Arguments',
                   'Date']
        rows = []
        for job in data:
            arguments = None if not job.batch.arguments else job.batch.arguments
            row = [job.id,
                   job.batch.config_model.name(),
                   job.exit_code,
                   arguments,
                   job.created_date]
            rows += [row]
        return (headers, rows)
