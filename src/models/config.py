import yaml
import os

from click import ClickException

class Config():
    def __init__(self, path):
        self.path = path
        def __read_data():
            with open(self.path, 'r') as stream:
                return yaml.load(stream) or {}
        self.data = __read_data()

    def __name__(self):
        return os.path.basename(os.path.dirname(self.path))

    def command(self):
        if 'command' not in self.data:
            raise ClickException('{} has no valid command'.format(self.__name__()))
        return self.data['command']

    def help(self):
        default = 'MISSING: Help for {}'.format(self.__name__())
        self.data.setdefault('help', default)
        return self.data['help']

    def families(self):
        default = ''
        self.data.setdefault('families', default)
        return self.data['families']
