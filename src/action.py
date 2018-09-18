
import glob
import click
import os
from models.batch import Batch

class ClickGlob:
    def command(click_group, namespace):
        def __glob_actions(namespace):
            parts = ['/var/lib/adminware/tools',
                     namespace, '*/config.yaml']
            paths = glob.glob(os.path.join(*parts))
            return list(map(lambda x: Action(x), paths))

        def __command(command_func):
            actions = __glob_actions(namespace)
            for action in actions:
                action.create(click_group, command_func)

        return __command



class Action:
    def __init__(self, path):
        self.path = path
        self.batch = Batch(config = self.path)

    def create(self, click_group, command_func):
        def action_func():
            return command_func(self.batch)
        action_func.__name__ = self.batch.__name__()
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click_group.command(help=self.batch.help())(func)

