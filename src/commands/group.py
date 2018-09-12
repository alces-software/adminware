
import click
import groups

def add_commands(appliance):

    @appliance.group(help='TODO')
    def group():
        pass

    @group.command(help='TODO')
    def list():
        click.echo("\n".join(groups.list()))

    @group.command(help='TODO')
    @click.argument('group_name')
    def show(group_name):
        pass
