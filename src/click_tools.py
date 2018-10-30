
import click
from os.path import basename

from explore_tools import each_dir, glob_all_configs, join_config
from models.config import Config

def command(click_group, namespace):
    def __command(command_func):
        each_dir(namespace,
                 __command_helper,
                 extra_args=[command_func],
                 parent_value = click_group)

    def __make_click_group(path, cur_group):
        new_namespace_bottom = basename(path)

        @cur_group.group(new_namespace_bottom,
                help="Descend into the {} namespace".format(new_namespace_bottom)
                )
        def new_group():
            pass

        return new_group

    def __command_helper(extra_args, config_exists, dir_path, parent_value):
        command_func = extra_args[0]
        if config_exists:
            action = Action(Config(join_config(dir_path)))
            action.create(parent_value, command_func)
        else:
            return __make_click_group(dir_path, parent_value)

    return __command

def command_family(click_group, namespace):
    def __command_family(command_func):
        for family in create_families(namespace):
            family.create(click_group, command_func)

    return __command_family

def create_families(namespace):
    configs = list(map(lambda x: Config(x), glob_all_configs(namespace)))
    ActionFamily.set_configs(configs)
    family_names = []
    for config in configs:
        if config.families(): family_names += config.families()
    # remove dupicates
    family_names = list(set(family_names))
    family_names.sort()
    families = list(map(lambda x: ActionFamily(x), family_names))
    return families

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
