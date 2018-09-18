
import click
from action import ClickGlob
from models.job import Job

# Note: this module cannot be called `open`, which would be consistent with
# other command modules, as this conflicts with Python's built-in `open`
# function.


def add_commands(appliance):

    @click.option('--node', '-n', required=True)
    @click.pass_context
    def open_command(ctx, **kwargs):
        ctx.obj = { 'adminware' : { 'node' : kwargs['node'] } }

    open_command.__name__ = 'open'
    open_command = appliance.group(help='TODO')(open_command)

    @ClickGlob.command(open_command, 'open')
    @click.pass_context
    def run_open(ctx, batch):
        job = Job(node = ctx.obj['adminware']['node'], batch = batch)
        job.run(interactive = True)

