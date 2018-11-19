
import click
from appliance_cli.command_generation import generate_commands
import command_creator
from appliance_cli.text import display_table

import cli_utils

from database import Session
from models.batch import Batch
from models.job import Job
import sqlalchemy

cmd_name = 'status'

def add_commands(appliance):
    options = {
        'options': {
            **cli_utils.hash__node__group,
            '--history': {
                'help': 'Return all the past results',
                'is_flag': True
            },
            ('--job', '-j'): {
                'help': 'Retrieve the result for the specified job',
                'metavar': 'JOB_ID',
                'type': int
            }
        }
    }

    short_help = { 'help': 'View past job results' }

    root_hash = {
        cmd_name: {
            **short_help,
            **options,
            'invoke_without_command': True,
            'pass_context': True,
            'commands': {}
        }
    }

    def root_status(c, _, *a): run_status(c, [], *a)

    generate_commands(appliance, root_hash, root_status)
    click_cmd = appliance.commands[cmd_name]

    status_cmd = {
        **short_help,
        **options
    }

    status_grp = {
        **short_help,
        **options,
        'invoke_without_command': True,
    }

    @command_creator.tools(click_cmd, command = status_cmd, group = status_grp)
    def _run_status(*a): run_status(*a)

    @cli_utils.ignore_parent_commands
    def run_status(ctx, _, argv, opts):
        job_id = opts['job'].value
        if isinstance(job_id, int): view_job(job_id)
        else: get_status(ctx, [], argv, opts)

    def view_job(job_id):
        job = Session().query(Job).get(job_id)
        if job == None: raise click.ClickException('No job found')
        table_data = [
            ['Date', job.created_date],
            ['Job ID', job.id],
            ['Node', job.node],
            ['Exit Code', job.exit_code],
            ['Tool', job.batch.name()],
            ['STDOUT', job.stdout],
            ['STDERR', job.stderr]
        ]
        display_table([], table_data)

    @cli_utils.with__node__group
    def get_status(_c, configs, _a, opts, nodes):
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
            row = [job.node,
                   job.batch.config_model.name(),
                   job.id,
                   job.exit_code,
                   job.created_date]
            if isinstance(job.count, int): row.append(job.count)
            rows += [row]

        display_table(headers, rows)

