
import click
import groups

def add_commands(appliance):

    @appliance.group(help='View the Adminware groups')
    def group():
        pass

    @group.command(help='Lists the possible groups')
    def list():
        click.echo_via_pager("\n".join(groups.list()))

    @group.command(help='Gives the nodes within a group')
    @click.argument('group_name')
    def show(group_name):
        click.echo_via_pager("\n".join(groups.nodes_in(group_name)))
