
import click
import explore_tools
from os.path import basename, join

def add_commands(appliance):
    @appliance.group(help='View the available tools')
    def avail():
        pass

    @avail.command(help='List available tools at a namespace')
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

    @avail.command(help='List all available tool families')
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

