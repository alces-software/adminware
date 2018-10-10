
import glob
import click
import re
from os import listdir
from os.path import join, dirname, relpath, isfile, isdir
from models.config import Config
from collections import defaultdict
from itertools import chain

class ClickGlob:
    #TODO possibly combine __glob_all_configs & __glob_dirs into one method to
    # ensure consistent results are generated. Likely with a decorator for __glob_dirs.
    def __glob_all_configs(namespace):
        #TODO DRY up the file leader - only define '/var/lib/adminware/tools' once
        parts = ['/var/lib/adminware/tools',
                 namespace, '**/config.yaml']
        paths = glob.glob(join(*parts), recursive=True)
        return list(map(lambda x: Config(x), paths))

    def __glob_dirs(namespace):
        parts = ['/var/lib/adminware/tools', namespace, '*']
        paths = glob.glob(join(*parts))
        return paths

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
                        raise RuntimeError("Directory detected sibling to a config.yaml file at {}\n".format(path)
                                + "This is invalid, please rectify it before continuing")

                    action = Action(Config('{}/config.yaml'.format(path)))
                    action.create(cur_group, command_func)
                else:
                    regex_expr = r'\/var\/lib\/adminware\/tools\/' + re.escape(cur_namespace) + r'\/(.*$)'
                    new_namespace_bottom = re.search(regex_expr, path).group(1)
                    new_namespace = join(cur_namespace, new_namespace_bottom)

                    if isdir(path):
                        @cur_group.group(new_namespace_bottom,
                                 help="Descend into the {} namespace".format(new_namespace_bottom)
                                 )
                        def new_group():
                            pass

                        __command_helper(new_group, new_namespace, command_func)

        return __command

    def command_family(click_group, namespace):
        def __command_family(command_func):
            configs = ClickGlob.__glob_all_configs(namespace)
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
