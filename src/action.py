
import glob
import click
import os
from models.config import Config
from collections import defaultdict
from itertools import chain

class ClickGlob:
    def __glob_actions(namespace):
        parts = ['/var/lib/adminware/tools',
                 namespace, '*/config.yaml']
        paths = glob.glob(os.path.join(*parts))
        return list(map(lambda x: Action(x), paths))

    def command(click_group, namespace):
        # command_func is either run_open or run_batch, what this is decorating
        def __command(command_func):
            actions = ClickGlob.__glob_actions(namespace)
            for action in actions:
                action.create(click_group, command_func)

        return __command

    def command_family(click_group, namespace):
        def __command_family(command_func):
            actions = ClickGlob.__glob_actions(namespace)
            families = []
            for action in actions:
                if action.get_families(): families += [action.get_families()]
            families_dict = __combine_dicts(families)
            for key in families_dict.keys():
                __create_option(click_group, command_func, key, families_dict[key])

        # when want to combine the family dictionaries - while concatenating duplicate values
        def __combine_dicts(dicts):
            families_dict = defaultdict(list)
            for single_dict in dicts:
                for k, v in single_dict.items():
                    families_dict[k].append(v)
            # sort each command family
            for key in families_dict:
                families_dict[key].sort()
            return families_dict

        def __create_option(click_group, command_func, family, commands):
            def action_family_func():
                return command_func(family, commands)
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
        # return a dict of each family this action is in, pointing to this action's name
        families = self.config.families()
        family_dict = {}
        for family in families:
            family_dict[family] = self.config.__name__()
        return family_dict

    def create(self, click_group, command_func):
        def action_func(arguments):
            return command_func(self.config, arguments)
        action_func.__name__ = self.config.__name__()
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click.argument('arguments', nargs=-1)(click_group.command(help=self.config.help())(func))

