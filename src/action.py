
import glob
import os

class Action:
    def __init__(self, path):
        self.path = path

    def name(self):
        return os.path.basename(os.path.dirname(self.path))


def add_actions(click_group, namespace):
    actions = __glob_actions(namespace)
    for action in actions:
        def _temp_f(action=action):
            print(action)
        _temp_f.__name__ = action.name()
        locals()[action] = _temp_f
        del _temp_f
        locals()[action] = click_group.command(help='TODO')(locals()[action])

def __glob_actions(namespace):
    parts = ['/var/lib/adminware/tools', namespace, '*/config.yaml']
    paths = glob.glob(os.path.join(*parts))
    return list(map(lambda x: Action(x), paths))

