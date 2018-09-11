
import appliance_cli.config
import appliance_cli.text as text


# Create Adminware CLI config object.


_APPLIANCE_TYPE = 'adminware'

_STANDARD_CONFIG = appliance_cli.config.create_config_dict(_APPLIANCE_TYPE)


def _support_eject_success_message(appliance_url=None):
    cli_info = text.line_wrap(
        'You may now log out and in again to gain full command-line access to '
        'the appliance.'
    )

    return cli_info

_ADMINWARE_CONFIG = {
    'SUPPORT_EJECT_INFO_MESSAGE': (
        'This will eject your Flight Adminware support, allowing you full '
        'command-line access via SSH.'
    ),
    'SUPPORT_EJECT_SUCCESS_MESSAGE_CALLBACK': _support_eject_success_message,
}

CONFIG = appliance_cli.config.finalize_config(
    _STANDARD_CONFIG, custom_config=_ADMINWARE_CONFIG
)
