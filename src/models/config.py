import yaml
import re
from os.path import basename, dirname
import subprocess

from config import TOOL_DIR

class Config():
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

    def additional_namespace(self):
        top_path = dirname(dirname(self.path))
        regex_expr = re.escape(TOOL_DIR) + r'(\/.*?$)'
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

