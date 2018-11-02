
import groups
from click import ClickException
from collections import OrderedDict

import re

def with__node__group(cmd_func):
    def __with__node__group(config, argv, options, *a):
        nodes = nodes_in__node__group(options)
        cmd_func(config, argv, options, nodes, *a)
    return __with__node__group

def nodes_in__node__group(options):
    nodes = groups.expand_nodes(options['node'].value)
    for group in options['group'].value:
        group_nodes = groups.nodes_in(group)
        if not group_nodes:
            raise ClickException('Could not find group: {}'.format(group))
        nodes.extend(group_nodes)
    return list(__remove_duplicates(nodes))

def strip_escaped_argv(func):
    def __strip_escaped_argv(c, argv, *a):
        parsed = list(map(lambda a: strip(a), argv))
        func(c, parsed, *a)

    def strip(string):
        return re.sub(r'^\\\s*', '', string)

    return __strip_escaped_argv

def set_nodes_context(ctx, **kwargs):
    # populate ctx.obj with nodes
    obj = { 'nodes' : [] }
    if kwargs['node']:
        obj['nodes'].extend(groups.expand_nodes(kwargs['node']))
    if kwargs['group']:
        for group in kwargs['group']:
            nodes = groups.nodes_in(group)
            if not nodes:
                raise ClickException('Could not find group: {}'.format(group))
            obj['nodes'].extend(nodes)
    obj['nodes'] = __remove_duplicates(obj['nodes'])
    ctx.obj = { 'adminware' : obj }

def __remove_duplicates(target_list):
    # gone for the slightly more intensive method that preserves order for pretty output
    return OrderedDict((x, True) for x in target_list).keys()
