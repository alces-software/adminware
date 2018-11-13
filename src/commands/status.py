
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
        if paths: tool_query = tool_query.filter(Batch.config.in_(paths))
        tool_subquery = tool_query.subquery()

        node_query = session.query(Job)
        if nodes: node_query = node_query.filter(Job.node.in_(nodes))
        node_subquery = node_query.subquery()

        columns = [
            node_subquery.c.id.label('id'),
            tool_subquery.c.config.label('config')
        ]
        id_query = session.query(*columns)\
                          .select_from(node_subquery)\
                          .join(tool_subquery)\
                          .subquery()

        max_func = sqlalchemy.func.max(Job.created_date)
        count_func = sqlalchemy.func.count()
        job_data = session.query(Job, max_func, count_func)\
                          .select_from(id_query)\
                          .filter(Job.id == id_query.c.id)\
                          .group_by(Job.node, id_query.c.config)\
                          .all()

        job_data = list(map(lambda d: [d[0], d[2]], job_data))
        if not job_data: raise click.ClickException('No jobs found')
        job_objects = [i for i, j in job_data]
        headers, rows = shared_job_data_table(job_objects)
        headers = headers + ['No. Runs']
        for i, (job, count) in enumerate(job_data):
            rows[i] = rows[i] + [count]
        # sort by first column
        rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    def shared_job_data_table(data):
        headers = ['Node',
                   'Tool',
                   'Job ID',
                   'Exit Code',
                   'Arguments',
                   'Date']
        rows = []
        for job in data:
            arguments = None if not job.batch.arguments else job.batch.arguments
            row = [job.node,
                   job.batch.config_model.name(),
                   job.id,
                   job.exit_code,
                   arguments,
                   job.created_date]
            rows += [row]
        return (headers, rows)

