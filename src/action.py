
import glob
import click
import re
import config

from sys import exit
from os import listdir
from os.path import join, isfile, isdir, basename
from models.config import Config


class ClickGlob:
    def __glob_dirs(namespace):
        new_dir = config.join_with_tool_location(namespace)
        if isdir(new_dir):
            parts = listdir(new_dir)
            paths = list(map(lambda x: join(new_dir, x), parts))
            return paths
        else:
            return []

    # function is either command_helper to generate Action objects & click commands
    #   or glob_helper to generate a list of all config paths (for ActionFamily & batch tools)
    def __each_dir(namespace, function, extra_args = [], parent_value = None):
        for dir_path in ClickGlob.__glob_dirs(namespace):
            config_exists = ClickGlob.__has_config(dir_path)
            child_value = function(extra_args,
                    config_exists = config_exists,
                    dir_path = dir_path,
                    parent_value = parent_value
                    )
            if not config_exists:
                new_namespace = dir_path[len(config.LEADER + config.TOOL_LOCATION):]
                ClickGlob.__each_dir(new_namespace, function, extra_args, parent_value = child_value)

    def glob_all(namespace):
        collector = []
        ClickGlob.__each_dir(namespace,
                ClickGlob.glob_helper,
                parent_value = collector)
        return collector

    def glob_helper(extra_args, config_exists, dir_path, parent_value):
        collector = parent_value
        if config_exists:
            collector += [dir_path]
        return collector

    def command(click_group, namespace):
        # command_func is either run_open or run_batch, what this is decorating
        def __command(command_func):
            ClickGlob.__each_dir(namespace,
                    command_helper,
                    extra_args=[command_func],
                    parent_value = click_group)

        def command_helper(extra_args, config_exists, dir_path, parent_value):
            #this seems a little suboptimal
            command_func = extra_args[0]
            if config_exists:
                action = Action(Config(ClickGlob.__join_config(dir_path)))
                action.create(parent_value, command_func)
            else:
                return ClickGlob.__make_group(dir_path, parent_value)

        return __command

    def command_family(click_group, namespace):
        def __command_family(command_func):
            configs = list(map(lambda x: Config(ClickGlob.__join_config(x)), ClickGlob.glob_all(namespace)))
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

    def __make_group(path, cur_group):
        new_namespace_bottom = basename(path)

        @cur_group.group(new_namespace_bottom,
                help="Descend into the {} namespace".format(new_namespace_bottom)
                )
        def new_group():
            pass

        return new_group

    def __join_config(path):
        return join(path, 'config.yaml')

    def __has_config(path):
        return isfile(ClickGlob.__join_config(path))


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
