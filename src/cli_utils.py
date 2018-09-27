
import groups
from click import ClickException

def set_nodes_context(ctx, **kwargs):
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
    ctx.obj = { 'adminware' : obj }
