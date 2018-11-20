
import click

from appliance_cli.commands import command_modules as standard_command_modules
from commands import run
from commands import view
from commands import status

@click.group(help='Perform Flight Adminware management tasks.')
def adminware():
    pass


command_modules = standard_command_modules + [
    run,
    view,
    status,
]

for module in command_modules:
    module.add_commands(adminware)
