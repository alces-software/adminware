import yaml
import os

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
        n = self.__name__()
        default = 'No command set'
        self.data.setdefault('command', default)
        return self.data['command']

    def help(self):
        default = 'MISSING: Help for {}'.format(self.__name__())
        self.data.setdefault('help', default)
        return self.data['help']

    def families(self):
        default = ''
        self.data.setdefault('families', default)
        return self.data['families']
