
import click

from appliance_cli.commands import command_modules as standard_command_modules


@click.group(help='Perform Flight Adminware management tasks.')
def adminware():
    pass


# No custom commands yet.
command_modules = standard_command_modules

for module in command_modules:
    module.add_commands(adminware)
