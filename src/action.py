
import glob
import click
import os
from models.config import Config

class ClickGlob:
    def glob_actions(namespace):
        parts = ['/var/lib/adminware/tools',
                 namespace, '*/config.yaml']
        paths = glob.glob(os.path.join(*parts))
        return list(map(lambda x: Action(x), paths))

    def command(click_group, namespace):
        # command_func is either run_open or run_batch, what this is decorating
        def __command(command_func):
            actions = ClickGlob.glob_actions(namespace)
            for action in actions:
                action.create(click_group, command_func)

        return __command

    def command_family(click_group, namespace):
        def __command_family(command_func):
            actions = ClickGlob.glob_actions(namespace)
            families = []
            for action in actions:
                if action.get_families(): families += action.get_families()
            families = list(set(families))
            for family in families:
                __create_option(click_group, command_func, family)

        def __create_option(click_group, command_func, family):
            def action_family_func():
                return command_func(family)
            action_family_func.__name__ = (family)
            action_family_func = click_group.command(
                    help='Run the command family \'{}\''.format(family)
                    )(action_family_func)

        return __command_family

class Action:
    def __init__(self, path):
        self.path = path
        self.config = Config(self.path)

    def get_families(self):
        return self.config.families()

    def create(self, click_group, command_func):
        def action_func(arguments):
            return command_func(self.config, arguments)
        action_func.__name__ = self.config.__name__()
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click.argument('arguments', nargs=-1)(click_group.command(help=self.config.help())(func))
