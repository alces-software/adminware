
from os import listdir
from os.path import join, isfile, isdir

import config
from models.config import Config

def glob_all_configs(namespace):
    def __glob_helper(extra_args, config_exists, dir_path, parent_value):
        collector = parent_value
        if config_exists:
            collector += [dir_path]
        return collector

    collector = []
    each_dir(namespace,
             __glob_helper,
             parent_value = collector)
    collector = list(map(join_config, collector))
    return collector

def inspect_namespace(namespace):
    paths = __glob_dirs(namespace)
    dir_contents = {'configs' : [], 'dirs' : []}
    for path in paths:
        if __has_config(path):
            dir_contents['configs'] += [Config(join_config(path))]
        elif isdir(path):
            dir_contents['dirs'] += [path]
    return dir_contents

# function is either command_helper to generate Action objects & click commands
#   or glob_helper to generate a list of all config paths (for ActionFamily & batch tools)
def each_dir(namespace, function, extra_args = [], parent_value = None):
    for dir_path in __glob_dirs(namespace):
        config_exists = __has_config(dir_path)
        child_value = function(extra_args,
                               config_exists = config_exists,
                               dir_path = dir_path,
                               parent_value = parent_value)
        if not config_exists:
            new_namespace = dir_path[len(config.LEADER + config.TOOL_LOCATION):]
            each_dir(new_namespace, function, extra_args, parent_value = child_value)

def __glob_dirs(namespace):
    new_dir = config.join_with_tool_location(namespace)
    if isdir(new_dir):
        parts = listdir(new_dir)
        paths = list(map(lambda x: join(new_dir, x), parts))
        return paths
    else:
        return []

def join_config(path):
    return join(path, 'config.yaml')

def __has_config(path):
    return isfile(join_config(path))
