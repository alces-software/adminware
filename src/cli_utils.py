
import groups
from click import ClickException
from collections import OrderedDict

def nodes_in__node__group_opts(options):
    nodes = groups.expand_nodes(options['node'].value)
    for group in options['group'].value:
        group_nodes = groups.nodes_in(group)
        if not group_nodes:
            raise ClickException('Could not find group: {}'.format(group))
        nodes.extend(group_nodes)
    return list(__remove_duplicates(nodes))

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
