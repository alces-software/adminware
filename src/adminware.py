
import click

from appliance_cli.commands import command_modules as standard_command_modules
import group
import batch
import open_command


@click.group(help='Perform Flight Adminware management tasks.')
def adminware():
    pass


command_modules = standard_command_modules + [
    batch,
    group,
    open_command,
]

for module in command_modules:
    module.add_commands(adminware)
