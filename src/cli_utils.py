
import groups
from click import ClickException
from collections import OrderedDict

def set_nodes_context(ctx, **kwargs):
    # populate ctx.obj with nodes
    obj = { 'nodes' : [] }
    if kwargs['node']:
        for node in kwargs['node']:
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
