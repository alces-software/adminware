
import click_tools
import explore_tools
import groups as groups_util

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

    @view.group(help="View a tool's details")
    def tool():
        pass

    @click_tools.command(tool)
    def get_tool_info(config, _a):
        table_data = [
            ['Name', config.name()],
            ['Description', config.help()],
            ['Shell Command', config.command()],
            ['Interactive', 'Yes' if config.interactive_only() else 'No'],
            ['Families', '\n'.join(config.families())],
            ['Working Directory', '\n'.join(config.working_files())]
        ]
        display_table([], table_data)

    @view.command(help='List available tools at a namespace')
    @click.argument('namespaces', nargs=-1, required=False)
    def tools(namespaces):
        if not namespaces: namespaces = ''
        namespace_path = '/'.join(namespaces)
        dir_contents = explore_tools.inspect_namespace(namespace_path)
        if dir_contents['configs'] or dir_contents['dirs']:
            output = ''
            for config in dir_contents['configs']:
                output = output + "\n{} -- {}\n".format(config.__name__(), config.help())
                if config.interactive_only(): output = output + "Only runnable interactively\n"
            for directory in dir_contents['dirs']:
                directory = os.path.basename(os.path.basename(directory))
                new_command_namespaces = ' '.join(tuple(namespaces) + (directory, ))
                output += "\n{} -- see 'view tools {}'\n".format(directory, new_command_namespaces)
        else:
            if namespaces:
                output = "No tools or subdirectories in '{}'".format('/'.join(namespaces))
            else:
                output = "No tools found"
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
            output = "No tool families have been configured"
        click.echo_via_pager(output)

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
        tool_data = session.query(Job, func.count(Batch.config))\
                           .filter(Job.node == node)\
                           .join("batch")\
                           .order_by(Job.created_date.desc())\
                           .group_by(Batch.config)\
                           .all()
        if not tool_data: raise ClickException('No jobs found for node {}'.format(node))
        headers, rows = gen_columns(tool_data)
        headers = ['Tool'] + headers
        for i, tool_datum in enumerate(tool_data):
            rows[i] = [tool_datum[0].batch.__name__()] + rows[i]
        # sort by first column
        rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    @view.group(name='tool-status', help='View the execution history of a single tool')
    def tool_status():
        pass

    @click_tools.command(tool_status, exclude_interactive_only = True)
    def tool_status_runner(config, _):
        session = Session()
        # Returns the most recent job for each node and the number of times the tool's been ran
        # => [(latest_job1, count1), (lastest_job2, count2), ...]
        node_data = session.query(Job, func.count(Job.node))\
                           .select_from(Batch)\
                           .filter(Batch.config == config.path)\
                           .join(Job.batch)\
                           .order_by(Job.created_date.desc())\
                           .group_by(Job.node)\
                           .all()
        if not node_data: raise ClickException('No jobs found for tool {}'.format(config.__name__()))
        headers, rows = gen_columns(node_data)
        headers = ['Node'] + headers
        for i, node_datum in enumerate(node_data):
            rows[i] = [node_datum[0].node] + rows[i]
        # sort by first column
        rows.sort(key=lambda x:x[0])
        display_table(headers, rows)

    def gen_columns(data):
        headers = ['Exit Code',
                    'Job ID',
                    'Arguments',
                    'Date',
                    'No. Runs']
        rows = []
        for job, count in data:
            arguments = None if not job.batch.arguments else job.batch.arguments
            row = [job.exit_code,
                   job.id,
                   arguments,
                   job.created_date,
                   count]
            rows += [row]
        return (headers, rows)
