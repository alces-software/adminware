
import groups as groups_util

from appliance_cli.text import display_table

import click
import click_tools
import explore_tools
from os.path import basename, join

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
        if job == None: raise ClickException('No job found')
        table_data = [
            ['Date', job.created_date],
            ['Batch ID', job.batch.id],
            ['Node', job.node],
            ['Exit Code', job.exit_code],
            ['Command', job.batch.__name__()],
            ['Arguments', job.batch.arguments],
            ['STDOUT', job.stdout],
            ['STDERR', job.stderr]
        ]
        display_table([], table_data)

    @view.command(help='List available tools at a namespace')
    @click.argument('namespace', required=False)
    def tools(namespace):
        if not namespace: namespace = ''
        dir_contents = explore_tools.inspect_namespace(namespace)
        if dir_contents['configs'] or dir_contents['dirs']:
            output = ''
            for config in dir_contents['configs']:
                output = output + "\n{} -- {}\n".format(config.__name__(), config.help())
                if config.interactive_only(): output = output + "Only runnable interactively\n"
            for directory in dir_contents['dirs']:
                directory = basename(directory)
                output += "\n{} -- see 'avail tools {}'\n".format(basename(directory),
                                                                  join(namespace,
                                                                  basename(directory)))
        else:
            if namespace:
                output = "No commands or subdirectories in '{}'".format(namespace)
            else:
                output = "No commands found"
        click.echo_via_pager(output)

    @view.command(help='List all available tool families')
    def families():
        action_families = click_tools.create_families('')
        if action_families:
            output = ''
            for family in action_families:
                output = output + "\n{}".format(family.name) + \
                         "\n{}\n".format(" --> ".join(list(map(lambda x: x.__name__(), family.get_members_configs()))))
        else:
            output = "No command families have been configured"
        click.echo_via_pager(output)

