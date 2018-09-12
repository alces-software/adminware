
import glob
import os

def add_actions(click_group, namespace):
    actions = __glob_actions(namespace)
    for action in sorted(actions):
        def _temp_f():
            print(action)
        _temp_f.__name__ = action
        locals()[action] = _temp_f
        del _temp_f
        locals()[action] = click_group.command(help='TODO')(locals()[action])


def __glob_actions(namespace):
    parts = ['/var/lib/adminware/tools', namespace, '*/config.yaml']
    paths = glob.glob(os.path.join(*parts))
    return dict(
        ((os.path.basename(os.path.dirname(p)), p) for p in paths)
    )

