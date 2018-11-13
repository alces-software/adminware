
import os.path
from glob import glob

import groups
import config
from models.config import Config
from appliance_cli.command_generation import generate_commands

def tool_commands(root_command, **kwargs):
    class ConfigCallback():
        def __init__(self, callback_func):
            self.callback = callback_func

        def run(self, callstack, *a, ctx):
            if not ctx.invoked_subcommand:
                parts = [config.TOOL_DIR, *callstack, '**/config.yaml']
                paths = glob(os.path.join(*parts), recursive = True)
                if not paths:
                    raise click.ClickException("""
No tools found in '{}'
""".format('/'.join(callstack)).strip())
                configs = list(map(lambda x: Config(x), paths))
                if wants_context:
                    self.callback(configs, *a, ctx = ctx)
                else:
                    self.callback(configs, *a)

    wants_context = False
    if kwargs['group'].get('pass_context')\
          or kwargs['command'].get('pass_context'):
        wants_context = True

    kwargs['group'].setdefault('pass_context', True)
    kwargs['command'].setdefault('pass_context', True)

    def __tool_commands(config_callback):
        config_hash = __hashify_all(subcommand_key = 'commands', **kwargs)
        callback = ConfigCallback(config_callback).run
        generate_commands(root_command, config_hash, callback)
    return __tool_commands

def __all_configs():
    glob_path = os.path.join(config.TOOL_DIR, '**/*/config.yaml')
    return list(map(lambda p: Config.cache(p), glob(glob_path, recursive=True)))

def __copy_values(source, target, args):
   for k, v in source.items():
       target[k] = (v(args) if callable(v) else v)

def group_commands(root_command, **kwargs):
    def __group_commands(callback):
        groups_hash = __hashify_all_groups(**kwargs)
        generate_commands(root_command, groups_hash, callback)
    return __group_commands

# The commands are hashed into the following structure
# NOTES: `command` and `group` both supports callable objects as a means
#        to customize the hashes. They are called with:
#          - command: The config object
#          - group: The current name
#   {
#       command1: **<command>,
#       namespace1: {
#           **<group>,
#           <subcommand_key>: {
#               command2: **<command>
#               ...
#           }
#       }
#   }
def __hashify_all(group = {}, command = {}, subcommand_key = ''):
    def build_group_hashes():
        cur_hash = combined_hash
        names = config.names()
        for idx, name in enumerate(config.names()):
            cur_names = names[0:idx]
            __copy_values(group, cur_hash, cur_names)
            cur_hash = cur_hash.setdefault(subcommand_key, {})\
                               .setdefault(name, {})
        return cur_hash

    combined_hash = {}
    for config in __all_configs():
        __copy_values(command, build_group_hashes(), config)

    return combined_hash[subcommand_key]

# Generates a similar hash to Config hasify func - for node groups
#   {
#       groupX: **<node>,
#       ...
#   }
def __hashify_all_groups(command = {}):
     combined_hash = {}
     for group in groups.list_groups():
         group_hash = combined_hash.setdefault(group, {})
         __copy_values(command, group_hash, group)
     return combined_hash
