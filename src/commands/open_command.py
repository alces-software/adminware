
import click

# Note: this module cannot be called `open`, which would be consistent with
# other command modules, as this conflicts with Python's built-in `open`
# function.


def add_commands(appliance):

    @appliance.group(help='TODO')
    @click.option('--node', '-n', required=True)
    def open():
        # XXX Add dynamic subcommands pulled from
        # `/var/lib/adminware/tools/open/` to this group
        pass
