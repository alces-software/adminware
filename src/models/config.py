import yaml
import re
from os.path import basename, dirname

import os.path
from glob import glob

from appliance_cli.command_generation import generate_commands

import subprocess

from functools import lru_cache

CONFIG_DIR = '/var/lib/adminware/tools'

class Config():
    def commands(root_command, **kwargs):
        class ConfigCallback():
            def __init__(self, callback_func):
                self.callback = callback_func

            def run(self, callstack, *a):
                path = os.path.join(CONFIG_DIR, *callstack, 'config.yaml')
                self.callback(Config(path), *a)

        def __commands(config_callback):
            config_hash = Config.hashify_all(subcommand_key = 'commands', **kwargs)
            callback = ConfigCallback(config_callback).run
            generate_commands(root_command, config_hash, callback)
        return __commands

    def family_commands(root_command, **kwargs):
        def __family_commands(callback):
            families_hash = Config.hashify_all_families(**kwargs)
            generate_commands(root_command, families_hash, callback)
        return __family_commands

    # lru_cache will cache the result of the `all` function. This prevents the Config
    # files being read more than once. However it also prevents updates and creations
    @lru_cache()
    def all():
        glob_path = os.path.join(CONFIG_DIR, '**/*/config.yaml')
        return list(map(lambda p: Config(p), glob(glob_path, recursive=True)))

    @lru_cache()
    def all_families():
        combined_hash = {}
        for config in Config.all():
            for family in config.families():
                combined_hash.setdefault(family, [])
                combined_hash[family] += [config]
        return combined_hash

    # The commands are hashed into the following structure
    # NOTES: `command` and `group both supports callable objects as a means
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
    def hashify_all(group = {}, command = {}, subcommand_key = ''):
        def build_group_hashes():
            cur_hash = combined_hash
            names = config.names()
            for idx, name in enumerate(config.names()):
                cur_names = names[0:idx]
                Config.__copy_values(group, cur_hash, cur_names)
                cur_hash = cur_hash.setdefault(subcommand_key, {})\
                                   .setdefault(name, {})
            return cur_hash

        combined_hash = {}
        for config in Config.all():
            Config.__copy_values(command, build_group_hashes(), config)

        return combined_hash[subcommand_key]

    # Generates a similar hash as above but for the command families
    # Callable objects are called with the family name
    #   {
    #       familyX: **<command>,
    #       ...
    #   }
    def hashify_all_families(command = {}):
        combined_hash = {}
        for family in Config.all_families():
            family_hash = combined_hash.setdefault(family, {})
            Config.__copy_values(command, family_hash, family)
        return combined_hash

    def __copy_values(source, target, args):
        for k, v in source.items():
            target[k] = (v(args) if callable(v) else v)

    def __init__(self, path):
        self.path = path
        def __read_data():
            with open(self.path, 'r') as stream:
                return yaml.load(stream) or {}
        self.data = __read_data()

    def __name__(self):
        return basename(dirname(self.path))

    def name(self):
        prefix = (self.additional_namespace() + ' ' if self.additional_namespace() else '')
        return "{}{}".format(prefix, self.__name__())

    def names(self):
        return self.name().split()

    def additional_namespace(self):
        top_path = dirname(dirname(self.path))
        regex_expr = re.escape(CONFIG_DIR) + r'(\/.*?$)'
        result = re.search(regex_expr, top_path)
        namespace_path = result.group(1) if result else ''
        return namespace_path.translate(namespace_path.maketrans('/', ' ')).strip()

    def command(self):
        default = 'MISSING: Command for {}'.format(self.__name__())
        self.data.setdefault('command', default)
        if not self.data['command']: self.data['command'] = default
        return self.data['command']

    def help(self):
        default = 'MISSING: Help for {}'.format(self.__name__())
        self.data.setdefault('help', default)
        if not self.data['help']: self.data['help'] = default
        return self.data['help']

    def families(self):
        default = ''
        self.data.setdefault('families', default)
        if not self.data['families']: self.data['families'] = default
        return self.data['families']

    # Deprecated, avoid usage
    def interactive_only(self):
        return self.interactive()

    def interactive(self):
        return 'interactive' in self.data and self.data['interactive'] == True

    def command_exists(self):
        return 'command' in self.data and self.data['command']

    def working_files(self):
        ls_cmd = 'ls {}'.format(dirname(self.path))
        stdout, _err = subprocess.Popen(ls_cmd, stdout=subprocess.PIPE, shell=True)\
                                 .communicate()
        working_files = stdout.decode("utf-8").rstrip('\n').split('\n')
        return list(map(lambda f: "./{}".format(f), working_files))

