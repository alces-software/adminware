
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
    @command_creator.groups(group, command = group_command)
    def get_group_info(_ctx, callstack, _a, _o):
        group_name = callstack[0]
        click.echo_via_pager("\n".join(groups_util.nodes_in(group_name)))

    @view.group(help="See more details about your tools")
    def tool():
        pass

    tool_cmd = { 'help': "See tool's details" }
    tool_grp = { 'help': 'List details for further tools' }
    @command_creator.tools(tool, command = tool_cmd, group = tool_grp)
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

