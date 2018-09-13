
import glob
import os

class Action:
    def __init__(self, path):
        self.path = path

    def __name__(self):
        return os.path.basename(os.path.dirname(self.path))

    def create(self, click_group):
        def action_func(self=self):
            print(self.name())
        action_func.__name__ = self.__name__()
        action_func = self.__click_func(action_func, click_group)

    # This method must be called after `create` to ensure the local
    # function has been defined
    def __click_func(self, func, click_group):
        return click_group.command(help='TODO')(func)

def add_actions(click_group, namespace):
    actions = __glob_actions(namespace)
    for action in actions:
        action.create(click_group)

def __glob_actions(namespace):
    parts = ['/var/lib/adminware/tools', namespace, '*/config.yaml']
    paths = glob.glob(os.path.join(*parts))
    return list(map(lambda x: Action(x), paths))

