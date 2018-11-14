
from appliance_cli.text import display_table
import click
import cli_utils

from database import Session
from models.batch import Batch
from models.job import Job
from models.config import Config

import groups

import sqlalchemy

from appliance_cli.command_generation import generate_commands

cmd_name = 'status'

def add_commands(appliance):
    def root_status(_c, argv, opts):
        get_status([], argv, opts)

    shared_options = {
        **cli_utils.hash__node__group,
        '--history': {
            'help': 'Return all the past results',
            'is_flag': True
        }
    }

    root_hash = {
        cmd_name: {
            'help': 'FIX MY TOP LEVEL HELP',
            'options': {
                **shared_options,
                ('--job', '-j'): {
                    'help': 'Retrieve the result for the specified job',
                    'metavar': 'JOB_ID',
                    'type': int
                }
            },
            'invoke_without_command': True,
            'commands': {}
        }
    }
    generate_commands(appliance, root_hash, root_status)
    click_cmd = appliance.commands[cmd_name]

    status_cmd = {
        'help': 'FIX ME',
        'options': shared_options
    }

    status_grp = {
        'help': 'FIX ME',
        'invoke_without_command': True,
        'options': shared_options
    }

    @Config.commands(click_cmd, command = status_cmd, group = status_grp)
    def get_tool_status(*a): get_status(*a)

    @cli_utils.with__node__group
    def get_status(configs, _a, opts, nodes, **a):
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

        def run_query(**k):
            def job_query(funcs = []):
                query = session.query(Job, *funcs)\
                               .select_from(id_query)\
                               .filter(Job.id == id_query.c.id)
                if funcs: query = query.group_by(Job.node, id_query.c.config)
                return query

            data = job_query(**k).all()
            if not data: raise click.ClickException('No jobs found')
            return data

        jobs = []
        headers = ['Node',
                   'Tool',
                   'Job ID',
                   'Exit Code',
                   'Arguments',
                   'Date']

        if opts['history'].value: jobs += run_query()
        else:
            # Query the db (including the job count)
            max_func = sqlalchemy.func.max(Job.created_date)
            count_func = sqlalchemy.func.count()
            raw_data = run_query(funcs = [max_func, count_func])

            # Store the counts on the job objects
            for (job, _, count) in raw_data:
                job.count = count
                jobs.append(job)

            # Add the count terminal table column
            headers.append('No. Runs')

        jobs.sort()

        rows = []
        for job in jobs:
            arguments = None if not job.batch.arguments else job.batch.arguments
            row = [job.node,
                   job.batch.config_model.name(),
                   job.id,
                   job.exit_code,
                   arguments,
                   job.created_date]
            if isinstance(job.count, int): row.append(job.count)
            rows += [row]

        display_table(headers, rows)

