
import glob
import click
import os
from models.config import Config

class ClickGlob:
    def command(click_group, namespace):
        def __glob_actions(namespace):
            parts = ['/var/lib/adminware/tools',
                     namespace, '*/config.yaml']
            paths = glob.glob(os.path.join(*parts))
            return list(map(lambda x: Action(x), paths))

        # command_func is either run_open or run_batch, what this is decorating
        def __command(command_func):
            actions = __glob_actions(namespace)
            for action in actions:
                action.create(click_group, command_func)

        return __command



class Action:
    def __init__(self, path):
        self.path = path
        self.config = Config(self.path)

    def create(self, click_group, command_func):
        def action_func(arguments):
            return command_func(self.config, arguments)
        action_func.__name__ = self.config.__name__()
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click.argument('arguments', nargs=-1)(click_group.command(help=self.config.help())(func))

