
import glob
import click
import re
import config

from sys import exit
from os import listdir
from os.path import join, dirname, relpath, isfile, isdir
from models.config import Config
from collections import defaultdict
from itertools import chain

class ClickGlob:
    def __glob_dirs(namespace):
        new_dir = join(config.LEADER, config.TOOL_LOCATION, namespace)
        if isdir(new_dir):
            parts = listdir(new_dir)
            paths = list(map(lambda x: join(new_dir, x), parts))
            return paths
        else:
            return []

    # decorator for __glob_dir to get all valid paths (ending in config.yaml) at once
    def __glob_all(globbing_func):
        def __wrapper(*args, **kwargs):
            def __sub_wrapper(*args, **kwargs):
                paths = globbing_func(*args)
                for path in paths:
                    if isfile('{}/config.yaml'.format(path)):
                        kwargs['all_paths'] += [join(path, 'config.yaml')]
                    else:
                        namespace = path[len(config.LEADER + config.TOOL_LOCATION):]
                        __sub_wrapper(namespace, **kwargs)
                return kwargs['all_paths']

            return __sub_wrapper(*args, **kwargs)

        return __wrapper

    def command(click_group, namespace):
        # command_func is either run_open or run_batch, what this is decorating
        def __command(command_func):
            __command_helper(click_group, namespace, command_func)

        def __command_helper(cur_group, cur_namespace, command_func):
            paths = ClickGlob.__glob_dirs(cur_namespace) # will generate a list of paths at level 'namespace'
            for path in paths:
                if isfile('{}/config.yaml'.format(path)):
                    # if there exists a sibling dir to any config.yaml this is currently an error
                    # TODO this will be removed with closure of issue #49 but more validation may be needed
                    if any(map(lambda x: isdir(join(path, x)), listdir(path))):
                        click.echo('config.yaml file with directory as sibling detected at {}\n'.format(path)
                                + 'This is invalid, please rectify it before continuing')
                        exit(1)

                    action = Action(Config('{}/config.yaml'.format(path)))
                    action.create(cur_group, command_func)
                else:
                    if isdir(path):
                        __command_helper(*ClickGlob.__make_group(path, cur_group, cur_namespace), command_func)

        return __command

    def command_family(click_group, namespace):
        def __command_family(command_func):
            __glob_all_dirs = ClickGlob.__glob_all(ClickGlob.__glob_dirs)
            configs = list(map(lambda x: Config(x), __glob_all_dirs(namespace, all_paths=[])))
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

    def __make_group(path, cur_group, cur_namespace):
        regex_expr = re.escape(config.LEADER) + \
                re.escape(config.TOOL_LOCATION) + \
                re.escape(cur_namespace) + \
                r'\/(.*$)'
        new_namespace_bottom = re.search(regex_expr, path).group(1)
        new_namespace = join(cur_namespace, new_namespace_bottom)

        @cur_group.group(new_namespace_bottom,
                help="Descend into the {} namespace".format(new_namespace_bottom)
                )
        def new_group():
            pass

        return (new_group, new_namespace)


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
