
import cli_utils
import groups as groups_util
import command_creator

from appliance_cli.text import display_table
from models.batch import Batch
from models.job import Job

import click
import os.path

from sqlalchemy import func
from database import Session
from models.job import Job

def add_commands(appliance):
    @appliance.group(help='View the available tools')
    def view():
        pass

    @view.group(help='Lists nodes within a group')
    def group():
        pass

    group_command = { 'help': 'View the nodes in this group' }
    @command_creator.group_commands(group, command = group_command)
    def get_group_info(_ctx, callstack, _a, _o):
        group_name = callstack[0]
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
            ['Tool', job.batch.__name__()],
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
    @command_creator.tool_commands(tool, command = tool_cmd, group = tool_grp)
    def get_tool_info(_ctx, configs, _a, _o):
        config = configs[0]
        table_data = [
            ['Name', config.name()],
            ['Description', config.help()],
            ['Shell Command', config.command()],
            ['Interactive', 'Yes' if config.interactive_only() else 'No'],
            ['Working Directory', '\n'.join(config.working_files())]
        ]
        display_table([], table_data)

