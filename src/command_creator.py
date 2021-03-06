
import os.path
import click
from glob import glob

import click

import groups as groups_util
import config
from models.config import Config
from appliance_cli.command_generation import generate_commands

from functools import lru_cache

def tools(root_command, **kwargs):
    class ConfigCallback():
        def __init__(self, callback_func):
            self.callback = callback_func

        def run(self, ctx, callstack, *a):
            configs = glob_configs(callstack)
            if not configs:
                raise click.ClickException("""
No tools found in '{}'
""".format('/'.join(callstack)).strip())
            self.callback(ctx, configs, *a)

    kwargs['group']['pass_context'] = True
    kwargs['command']['pass_context'] = True

    def _tools(config_callback):
        config_hash = _hashify_all(subcommand_key = 'commands', **kwargs)
        callback = ConfigCallback(config_callback).run
        generate_commands(root_command, config_hash, callback)
    return _tools

def groups(root_command, **kwargs):
    kwargs['command']['pass_context'] = True

    def _groups(callback):
        groups_hash = _hashify_all_groups(**kwargs)
        generate_commands(root_command, groups_hash, callback)
    return _groups

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
def _hashify_all(group = {}, command = {}, subcommand_key = ''):
    def build_group_hashes():
        cur_hash = combined_hash
        names = config.names()
        for idx, name in enumerate(config.names()):
            cur_names = names[0:idx]
            _copy_values(group, cur_hash, cur_names)
            cur_hash = cur_hash.setdefault(subcommand_key, {})\
                               .setdefault(name, {})
        return cur_hash

    combined_hash = {}
    for config in glob_configs():
        _copy_values(command, build_group_hashes(), config)

    return combined_hash.setdefault(subcommand_key, {})

@lru_cache()
def _glob_paths(*parts):
    path = os.path.join(config.TOOL_DIR, *parts, '**/config.yaml')
    return glob(path, recursive=True)

def glob_configs(parts = []):
    return list(map(lambda p: Config.cache(p), _glob_paths(*parts)))

# Generates a similar hash to Config hasify func - for node groups
#   {
#       groupX: **<node>,
#       ...
#   }
def _hashify_all_groups(command = {}):
     combined_hash = {}
     for group in groups_util.list_():
         group_hash = combined_hash.setdefault(group, {})
         _copy_values(command, group_hash, group)
     return combined_hash

def _copy_values(source, target, args):
   for k, v in source.items():
       target[k] = (v(args) if callable(v) else v)
