
from os import listdir
from os.path import join, isfile, isdir, basename

import config
from models.config import Config
from action import Action, ActionFamily


def command(click_group, namespace):
    # command_func is either run_open or run_batch, what this is decorating
    def __command(command_func):
        __each_dir(namespace,
                   __command_helper,
                   extra_args=[command_func],
                   parent_value = click_group)

    def __command_helper(extra_args, config_exists, dir_path, parent_value):
        command_func = extra_args[0]
        if config_exists:
            action = Action(Config(__join_config(dir_path)))
            action.create(parent_value, command_func)
        else:
            return __make_group(dir_path, parent_value)

    return __command

def command_family(click_group, namespace):
    # command_func is run_batch_family, what this is decorating
    def __command_family(command_func):
        for family in create_families(namespace):
            family.create(click_group, command_func)

    return __command_family

def create_families(namespace):
    configs = list(map(lambda x: Config(x), __glob_all(namespace)))
    family_names = []
    for config in configs:
        if config.families(): family_names += config.families()
    # remove dupicates
    family_names = list(set(family_names))
    families = list(map(lambda x: ActionFamily(x), family_names))
    ActionFamily.set_configs(configs)
    return families

def __glob_all(namespace):
    def __glob_helper(extra_args, config_exists, dir_path, parent_value):
        collector = parent_value
        if config_exists:
            collector += [dir_path]
        return collector

    collector = []
    __each_dir(namespace,
               __glob_helper,
               parent_value = collector)
    collector = list(map(__join_config, collector))
    return collector

def single_level(namespace):
    paths = __glob_dirs(namespace)
    dir_contents = {'configs' : [], 'dirs' : []}
    for path in paths:
        if __has_config(path):
            dir_contents['configs'] += [Config(__join_config(path))]
        elif isdir(path):
            dir_contents['dirs'] += [path]
    return dir_contents

# function is either command_helper to generate Action objects & click commands
#   or glob_helper to generate a list of all config paths (for ActionFamily & batch tools)
def __each_dir(namespace, function, extra_args = [], parent_value = None):
    for dir_path in __glob_dirs(namespace):
        config_exists = __has_config(dir_path)
        child_value = function(extra_args,
                               config_exists = config_exists,
                               dir_path = dir_path,
                               parent_value = parent_value)
        if not config_exists:
            new_namespace = dir_path[len(config.LEADER + config.TOOL_LOCATION):]
            __each_dir(new_namespace, function, extra_args, parent_value = child_value)

def __glob_dirs(namespace):
    new_dir = config.join_with_tool_location(namespace)
    if isdir(new_dir):
        parts = listdir(new_dir)
        paths = list(map(lambda x: join(new_dir, x), parts))
        return paths
    else:
        return []

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
    return isfile(__join_config(path))

