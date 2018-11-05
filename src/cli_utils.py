
import groups
from models.config import Config
from click import ClickException
from collections import OrderedDict

import re

def with__node__group(cmd_func):
    def __with__node__group(config, argv, options, *a):
        nodes = nodes_in__node__group(options)
        cmd_func(config, argv, options, *a, nodes)
    return __with__node__group

def nodes_in__node__group(options):
    nodes = groups.expand_nodes(options['node'].value)
    for group in options['group'].value:
        try:
            group_nodes = Config.all_groups()[group]
        except KeyError:
            raise ClickException('Could not find group: {}'.format(group))
        nodes.extend(group_nodes)
    return list(__remove_duplicates(nodes))

def __remove_duplicates(target_list):
    # gone for the slightly more intensive method that preserves order for pretty output
    return OrderedDict((x, True) for x in target_list).keys()
