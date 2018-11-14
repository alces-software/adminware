import yaml
import re
import click
import os.path
import subprocess
from os.path import basename, dirname
from collections import defaultdict
from functools import lru_cache

import config

class Config():
    def __init__(self, path):
        self.path = path
        def __read_data():
            with open(self.path, 'r') as stream:
                return yaml.load(stream) or {}
        if os.path.isfile(path):
            self.data = __read_data()
        else:
            self.data = defaultdict(lambda: 'File not found')

    @lru_cache()
    def cache(*a, **kw): return Config(*a, **kw)

    def __name__(self):
        return basename(dirname(self.path))

    def name(self):
        prefix = (self.additional_namespace() + ' ' if self.additional_namespace() else '')
        return "{}{}".format(prefix, self.__name__())

    def names(self):
        return self.name().split()

    def additional_namespace(self):
        top_path = dirname(dirname(self.path))
        regex_expr = re.escape(config.TOOL_DIR) + r'(\/.*?$)'
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

