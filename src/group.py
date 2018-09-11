
import click


def add_commands(appliance):

    @appliance.group(help='TODO')
    def group():
        pass

    @group.command(help='TODO')
    @click.argument('group_name')
    def list(group_name):
        pass

    @group.command(help='TODO')
    @click.argument('group_name')
    def show(group_name):
        pass
