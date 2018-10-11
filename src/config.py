
import appliance_cli.config
import appliance_cli.text as text

from os.path import join


# Create Adminware CLI config object.
# Nothing special here for now, possibly overcomplicated due to adapting from
# bootstrapped legacy appliance CLI.


_APPLIANCE_TYPE = 'adminware'

_STANDARD_CONFIG = appliance_cli.config.create_config_dict(_APPLIANCE_TYPE)

CONFIG = appliance_cli.config.finalize_config(_STANDARD_CONFIG)

LEADER = '/var/lib/adminware/'

TOOL_LOCATION = 'tools/'

def join_with_tool_location(namespace):
    return join(LEADER, TOOL_LOCATION, namespace)
