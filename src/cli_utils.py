
import groups
from click import ClickException
from collections import OrderedDict

import re

hash__node__group = {
    ('--node', '-n'): {
        'help': 'Specify a node, repeat the flag for multiple',
        'multiple': True,
        'metavar': 'NODE'
    },
    ('--group', '-g'): {
        'help': 'Specify a group, repeat the flag for multiple',
        'multiple': True,
        'metavar': 'GROUP'
    }
}

def with__node__group(cmd_func):
    def _with__node__group(ctx, config, argv, options, *a):
        nodes = nodes_in__node__group(options)
        cmd_func(ctx, config, argv, options, *a, nodes)
    return _with__node__group

def nodes_in__node__group(options):
    nodes = groups.expand_nodes(options['node'].value)
    for group in options['group'].value:
        group_nodes = groups.nodes_in(group)
        if not group_nodes:
            raise ClickException('Could not find group: {}'.format(group))
        nodes.extend(group_nodes)
    return list(_remove_duplicates(nodes))

def _remove_duplicates(target_list):
    # gone for the slightly more intensive method that preserves order for pretty output
    return OrderedDict((x, True) for x in target_list).keys()

def ignore_parent_commands(func):
    def _wrapper(ctx, *args, **kwargs):
        if not ctx.invoked_subcommand:
            func(ctx, *args, **kwargs)
    return _wrapper
