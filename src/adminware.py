
import click

from appliance_cli.commands import command_modules as standard_command_modules
from commands import group
from commands import batch
from commands import open_command


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
