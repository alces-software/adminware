
import click

from appliance_cli.commands import command_modules as standard_command_modules
from commands import group
from commands import job
from commands import run

@click.group(help='Perform Flight Adminware management tasks.')
def adminware():
    pass


command_modules = standard_command_modules + [
    job,
    group,
    run,
]

for module in command_modules:
    module.add_commands(adminware)
