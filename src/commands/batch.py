
import click


def add_commands(appliance):

    @appliance.group(help='TODO')
    def batch():
        pass

    @batch.command(help='TODO')
    @click.option('--node', '-n')
    @click.option('--group', '-g')
    @click.option('--job-id', '-j')
    def history(**options):
        pass

    @batch.command(help='TODO')
    @click.argument('job_id')
    @click.argument('node')
    def view(job_id, node):
        pass

    @batch.group(help='TODO')
    @click.option('--node', '-n')
    @click.option('--group', '-g')
    def run():
        # XXX Add dynamic subcommands pulled from
        # `/var/lib/adminware/tools/batch/` to this group
        pass