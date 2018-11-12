import yaml
import re
import click
from os.path import basename, dirname

from collections import defaultdict
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

            def run(self, callstack, *a, ctx = None):
                if not ctx:
                    path = os.path.join(CONFIG_DIR, *callstack, 'config.yaml')
                    self.callback([Config(path)], *a)
                if ctx and not ctx.invoked_subcommand:
                    parts = [CONFIG_DIR, *callstack, '**/*/config.yaml']
                    paths = glob(os.path.join(*parts), recursive = True)
                    if not paths:
                        raise click.ClickException("""
No tools found in '{}'
""".format('/'.join(callstack)).strip())
                    configs = list(map(lambda x: Config(x), paths))
                    self.callback(configs, *a)

        def __commands(config_callback):
            config_hash = Config.hashify_all(subcommand_key = 'commands', **kwargs)
            callback = ConfigCallback(config_callback).run
            generate_commands(root_command, config_hash, callback)
        return __commands

    @lru_cache()
    def cache(*a, **kw): return Config(*a, **kw)

    def all():
        glob_path = os.path.join(CONFIG_DIR, '**/*/config.yaml')
        return list(map(lambda p: Config.cache(p), glob(glob_path, recursive=True)))

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

    def __copy_values(source, target, args):
        for k, v in source.items():
            target[k] = (v(args) if callable(v) else v)

    def __init__(self, path):
        self.path = path
        def __read_data():
            with open(self.path, 'r') as stream:
                return yaml.load(stream) or {}
        if os.path.isfile(path):
            self.data = __read_data()
        else:
            self.data = defaultdict(lambda: 'File not found')

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

    # TODO: Deprecated, avoid usage
    def interactive_only(self):
        return self.interactive()

    def __getattr__(self, attr):
        return self.data.setdefault(attr)

    # TODO: Use __getattr__ here
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

