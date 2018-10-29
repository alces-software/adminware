
import click

from appliance_cli.commands import command_modules as standard_command_modules
from commands import group
from commands import job


@click.group(help='Perform Flight Adminware management tasks.')
def adminware():
    pass


command_modules = standard_command_modules + [
    job,
    group,
]

for module in command_modules:
    module.add_commands(adminware)
