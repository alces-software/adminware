
import glob
import os
import yaml

class Action:
    def __init__(self, path):
        self.path = path
        def __read_data():
            with open(self.path, 'r') as stream:
                return yaml.load(stream) or {}
        self.data = __read_data()

    def __name__(self):
        return os.path.basename(os.path.dirname(self.path))

    def create(self, click_group):
        def action_func(self=self):
            print(self.command())
        action_func.__name__ = self.__name__()
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click_group.command(help=self.help())(func)

    def help(self):
        default = 'MISSING: Help for {}'.format(self.__name__())
        self.data.setdefault('help', default)
        return self.data['help']

    def command(self):
        n = self.__name__()
        default = 'echo "No command given for: {}" >&2'.format(n)
        self.data.setdefault('command', default)
        return self.data['command']

def add_actions(click_group, namespace):
    actions = __glob_actions(namespace)
    for action in actions:
        action.create(click_group)

def __glob_actions(namespace):
    parts = ['/var/lib/adminware/tools', namespace, '*/config.yaml']
    paths = glob.glob(os.path.join(*parts))
    return list(map(lambda x: Action(x), paths))

