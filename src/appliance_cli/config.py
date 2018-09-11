
from os.path import join

from appliance_cli.utils import struct

# Functions to create config object for an appliance CLI.


def create_config_dict(appliance_type):
    appliance_dir = join('/opt/', appliance_type)
    clusterware_root = '/opt/clusterware'

    return {
        'APPLIANCE_TYPE': appliance_type,
        'APPLIANCE_DIR': appliance_dir,
        'APPLIANCE_CONFIG': join(appliance_dir, 'etc/config'),

        'SANDBOX_HISTORY': join(appliance_dir, 'history'),

        'CLUSTERWARE_ROOT': clusterware_root,
        'CLUSTERWARE_ACCESS_CONFIG': join(clusterware_root, 'etc/access.rc'),

        'ACCESS_FQDN_KEY': 'cw_ACCESS_fqdn',
    }


# None for now, possibly just legacy after bootstrapping in same way as old
# appliance CLIs.
REQUIRED_CONFIG_VALUE_NAMES = []


def finalize_config(config_dict, custom_config=None):
    if custom_config:
        config_dict = {**config_dict, **custom_config}

    # All required config values must be provided by the client when creating
    # the config object.
    for key_name in REQUIRED_CONFIG_VALUE_NAMES:
        if key_name not in custom_config.keys():
            raise Exception(
                "Required config value '{}' not provided.".format(key_name)
            )

    return struct(config_dict)
