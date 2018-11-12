
from appliance_cli.text import display_table
import click

from database import Session
from models.batch import Batch
from models.job import Job
from models.config import Config

import sqlalchemy

def add_commands(appliance):
    @appliance.command(help='FIX ME')
    @click.argument('node', type=str)
    def status(node):
        session = Session()
        # Returns the most recent job for each tool and number of times it's been ran
        # Refs: https://docs.sqlalchemy.org/en/latest/core/functions.html#sqlalchemy.sql.functions.count
        #       https://www.w3schools.com/sql/func_sqlserver_count.asp
        # => [(latest_job1, count1), (lastest_job2, count2), ...]
        job_data = session.query(Job, sqlalchemy.func.count(Batch.config))\
                           .filter(Job.node == node)\
                           .join("batch")\
                           .order_by(Job.created_date.desc())\
                           .group_by(Batch.config)\
                           .all()
        if not job_data: raise click.ClickException('No jobs found for node {}'.format(node))
        job_objects = [i for i, j in job_data]
        headers, rows = shared_job_data_table(job_objects)
        headers = ['Tool'] + headers + ['No. Runs']
        for i, (job, count) in enumerate(job_data):
            rows[i] = [job.batch.__name__()] + rows[i] + [count]
        # sort by first column
        rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    def shared_job_data_table(data):
        headers = ['Job ID',
                   'Exit Code',
                   'Arguments',
                   'Date']
        rows = []
        for job in data:
            arguments = None if not job.batch.arguments else job.batch.arguments
            row = [job.id,
                   job.exit_code,
                   arguments,
                   job.created_date]
            rows += [row]
        return (headers, rows)
