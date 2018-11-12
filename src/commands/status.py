
from appliance_cli.text import display_table
import click
import cli_utils

from database import Session
from models.batch import Batch
from models.job import Job
from models.config import Config

import groups

import sqlalchemy

def add_commands(appliance):
    status_cmd = {
        'help': 'FIX ME',
        'options': cli_utils.hash__node__group
    }

    status_grp = {
        'help': 'FIX ME',
        'invoke_without_command': True,
        'options': cli_utils.hash__node__group,
    }

    @appliance.group(help='FIX ME')
    def status():
        pass

    @Config.commands(status, command = status_cmd, group = status_grp)
    @cli_utils.with__node__group
    def get_status(configs, _a, _o, nodes):
        session = Session()

        paths = list(map(lambda c: c.path, configs))
        tool_query = session.query(Batch)
        if paths: tool_query.filter(Batch.config.in_(paths))

        node_query = session.query(Job)
        if nodes: node_query.filter(Job.node.in_(nodes))

        subquery = node_query.join(tool_query)

        job_data = list(map(lambda j: [j, None], subquery.all()))
        if not job_data: raise click.ClickException('No jobs found for node {}'.format(nodes))
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
                   'Node',
                   'Tool',
                   'Exit Code',
                   'Arguments',
                   'Date']
        rows = []
        for job in data:
            arguments = None if not job.batch.arguments else job.batch.arguments
            row = [job.id,
                   job.node,
                   job.batch.config_model.name(),
                   job.exit_code,
                   arguments,
                   job.created_date]
            rows += [row]
        return (headers, rows)

