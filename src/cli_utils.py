
import groups
import re
from click import ClickException
from collections import OrderedDict

def set_nodes_context(ctx, **kwargs):
    # populate ctx.obj with nodes
    obj = { 'nodes' : [] }
    if kwargs['node']:
        for node in kwargs['node']:
            if re.match(r'.*\[[0-9]+-[0-9]+\]$', node):
                obj['nodes'] += __add_multiple_nodes(node)
            else:
                obj['nodes'].append(node)
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

def __add_multiple_nodes(nodes):
    prefix = re.sub(r'\[.*?$', '', nodes)
    num_2 = re.search(r'-([0-9]+)]$', nodes).group(1)
    num_1 = re.search(r'\[([0-9]+)-[0-9]+\]$', nodes).group(1)
    if (num_1 > num_2) or not num_1.isdigit() or not num_2.isdigit():
        raise ClickException('Invalid node range - {}{} to {}{}'.format(prefix, num_1, prefix, num_2))
    else:
        mid = ''
        # allowing for padding 0s in the range
        if re.match(r'^0', num_1):
            mid = re.search(r'^(0+)', num_1).group(1)
        nodes_list = []
        i = int(num_1)
        while i <= int(num_2):
            nodes_list += [prefix + mid + str(i)]
            i += 1
        return nodes_list
