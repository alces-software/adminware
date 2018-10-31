
import appliance_cli.config
import appliance_cli.text as text

import os.path


# Create Adminware CLI config object.
# Nothing special here for now, possibly overcomplicated due to adapting from
# bootstrapped legacy appliance CLI.


_APPLIANCE_TYPE = 'adminware'

_STANDARD_CONFIG = appliance_cli.config.create_config_dict(_APPLIANCE_TYPE)

CONFIG = appliance_cli.config.finalize_config(_STANDARD_CONFIG)

LEADER = '/var/lib/adminware/'

TOOL_LOCATION = 'tools/'

TOOL_DIR = os.path.join(LEADER, TOOL_LOCATION).strip('/')

def join_with_tool_location(namespace):
    return os.path.join(LEADER, TOOL_LOCATION, namespace)
