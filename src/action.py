
import glob
import click
import os
from models.config import Config
from collections import defaultdict
from itertools import chain

class ClickGlob:
    def __glob_configs(namespace):
        parts = ['/var/lib/adminware/tools',
                 namespace, '*/config.yaml']
        paths = glob.glob(os.path.join(*parts))
        return list(map(lambda x: Config(x), paths))

    def command(click_group, namespace):
        # command_func is either run_open or run_batch, what this is decorating
        def __command(command_func):
            actions = list(map(lambda x: Action(x), ClickGlob.__glob_configs(namespace)))
            for action in actions:
                action.create(click_group, command_func)

        return __command

    def command_family(click_group, namespace):
        def __command_family(command_func):
            configs = ClickGlob.__glob_configs(namespace)
            family_names = []
            for config in configs:
                if config.families(): family_names += config.families()
            # remove dupicates
            familiy_names = list(set(family_names))
            families = list(map(lambda x: ActionFamily(x), family_names))
            ActionFamily.set_configs(configs)
            for family in families:
                family.create(click_group, command_func)

        return __command_family

class Action:
    def __init__(self, config):
        self.config = config

    def create(self, click_group, command_func):
        def action_func(arguments):
            return command_func(self.config, arguments)
        action_func.__name__ = self.config.__name__()
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click.argument('arguments', nargs=-1)(click_group.command(help=self.config.help())(func))


class ActionFamily:
    configs = []

    def __init__(self, name):
        self.name = name

    def set_configs(configs):
        ActionFamily.configs = configs

    def get_members_configs(self):
        members_configs = []
        for config in ActionFamily.configs:
            if self.name in config.families():
                members_configs += [config]
        return members_configs

    def create(self, click_group, command_func):
        def action_family_func():
            return command_func(self.name, self.get_members_configs())
        action_family_func.__name__ = self.name
        action_family_func = click_group.command(
             help='Run the command family \'{}\''.format(self.name)
             )(action_family_func)
