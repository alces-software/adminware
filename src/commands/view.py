
import cli_utils
import groups as groups_util

from appliance_cli.text import display_table
from models.batch import Batch
from models.job import Job
from models.config import Config

import click
import os.path

from click import ClickException
from sqlalchemy import func
from database import Session
from models.job import Job

def add_commands(appliance):
    @appliance.group(help='View the available tools')
    def view():
        pass

    @view.command(help='Lists the available groups')
    def groups():
        click.echo_via_pager("\n".join(groups_util.list()))

    @view.command(help='Lists the nodes within a group')
    @click.argument('group_name')
    def group(group_name):
        click.echo_via_pager("\n".join(groups_util.nodes_in(group_name)))

    @view.command(help='View the result from a previous job')
    @click.argument('job_id', type=int)
    def result(job_id):
        job = Session().query(Job).get(job_id)
        if job == None: raise click.ClickException('No job found')
        table_data = [
            ['Date', job.created_date],
            ['Job ID', job.id],
            ['Node', job.node],
            ['Exit Code', job.exit_code],
            ['Command', job.batch.__name__()],
            ['Arguments', job.batch.arguments],
            ['STDOUT', job.stdout],
            ['STDERR', job.stderr]
        ]
        display_table([], table_data)

    @view.group(help="See more details about your tools")
    def tool():
        pass

    tool_cmd = { 'help': "See tool's details" }
    tool_grp = { 'help': 'List details for further tools' }
    @Config.commands(tool, command = tool_cmd, group = tool_grp)
    def get_tool_info(config, _a, _o):
        table_data = [
            ['Name', config.name()],
            ['Description', config.help()],
            ['Shell Command', config.command()],
            ['Interactive', 'Yes' if config.interactive_only() else 'No'],
            ['Families', '\n'.join(config.families())],
            ['Working Directory', '\n'.join(config.working_files())]
        ]
        display_table([], table_data)

    @view.command(name='node-status', help='View the execution history of a single node')
    @click.argument('node', type=str)
    # note: this works on config location, not command name.
    # Any commands that are moved will be considered distinct.
    def node_status(node):
        session = Session()
        # Returns the most recent job for each tool and number of times it's been ran
        # Refs: https://docs.sqlalchemy.org/en/latest/core/functions.html#sqlalchemy.sql.functions.count
        #       https://www.w3schools.com/sql/func_sqlserver_count.asp
        # => [(latest_job1, count1), (lastest_job2, count2), ...]
        job_data = session.query(Job, func.count(Batch.config))\
                           .filter(Job.node == node)\
                           .join("batch")\
                           .order_by(Job.created_date.desc())\
                           .group_by(Batch.config)\
                           .all()
        if not job_data: raise ClickException('No jobs found for node {}'.format(node))
        job_objects = [i for i, j in job_data]
        headers, rows = shared_job_data_table(job_objects)
        headers = ['Tool'] + headers + ['No. Runs']
        for i, (job, count) in enumerate(job_data):
            rows[i] = [job.batch.__name__()] + rows[i] + [count]
        # sort by first column
        rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    @view.group(name='tool-status', help='View the execution history of a single tool')
    def tool_status():
        pass

    tool_status_cmd = { 'help': 'List the status across the nodes' }
    tool_status_grp = { 'help': 'See the status of further tools' }
    @Config.commands(tool_status, command = tool_status_cmd, group = tool_status_grp)
    def tool_status_runner(config, _a, _o):
        session = Session()
        # Returns the most recent job for each node and the number of times the tool's been ran
        # => [(latest_job1, count1), (lastest_job2, count2), ...]
        job_data = session.query(Job, func.count(Job.node))\
                           .select_from(Batch)\
                           .filter(Batch.config == config.path)\
                           .join(Job.batch)\
                           .order_by(Job.created_date.desc())\
                           .group_by(Job.node)\
                           .all()
        if not job_data: raise ClickException('No jobs found for tool {}'.format(config.__name__()))
        job_objects = [i for i, j in job_data]
        headers, rows = shared_job_data_table(job_objects)
        headers = ['Node'] + headers + ['No. Runs']
        for i, (job, count) in enumerate(job_data):
            rows[i] = [job.node] + rows[i] + [count]
        # sort by first column
        rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    @view.command(name='node-history', help='View all executions on a single node')
    @click.argument('node', type=str)
    def node_history(node):
        session = Session()
        job_data = session.query(Job)\
                          .filter(Job.node == node)\
                          .join("batch")\
                          .all()
        if not job_data: raise ClickException('No jobs found for node {}'.format(node))
        headers, rows = shared_job_data_table(job_data)
        headers = ['Tool'] + headers
        for i, job in enumerate(job_data):
            rows[i] = [job.batch.__name__()] + rows[i]
        rows.sort(key=lambda x:x[1], reverse=True)
        display_table(headers, rows)

    @view.group(name='tool-history', help='View all executions of a single tool')
    def tool_history():
        pass

    @click_tools.command(tool_history, exclude_interactive_only = True)
    def tool_history_runner(config, _):
        session = Session()
        job_data = session.query(Job)\
                          .select_from(Batch)\
                          .filter(Batch.config == config.path)\
                          .join(Job.batch)\
                          .all()
        if not job_data: raise ClickException('No jobs found for tool {}'.format(config.__name__()))
        headers, rows = shared_job_data_table(job_data)
        headers = ['Node'] + headers
        for i, job in enumerate(job_data):
            rows[i] = [job.node] + rows[i]
        rows.sort(key=lambda x:x[1], reverse=True)
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
