
import click
from action import ClickGlob
from models.job import Job
from models.batch import Batch

# Note: this module cannot be called `open`, which would be consistent with
# other command modules, as this conflicts with Python's built-in `open`
# function.


def add_commands(appliance):

    @click.option('--node', '-n', required=True, metavar='NODE',
                  help='Runs the command on NODE')
    @click.pass_context
    def open_command(ctx, **kwargs):
        ctx.obj = { 'adminware' : { 'node' : kwargs['node'] } }

    open_command.__name__ = 'open'
    open_command = appliance.group(
                       help='Runs the command in an interactive shell'
                   )(open_command)

    @ClickGlob.command(open_command, 'open')
    @click.pass_context
    def run_open(ctx, config):
        batch = Batch(config = config.path)
        job = Job(node = ctx.obj['adminware']['node'], batch = batch)
        job.run(interactive = True)

