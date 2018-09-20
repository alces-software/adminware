
import groups
from click import ClickException

def set_nodes_context(ctx, **kwargs):
    obj = { 'nodes' : [] }
    if kwargs['node']: obj['nodes'].append(kwargs['node'])
    if kwargs['group']:
        group = kwargs['group']
        nodes = groups.nodes_in(group)
        if not nodes:
            raise ClickException('Could not find group: {}'.format(group))
        obj['nodes'].extend(nodes)
    ctx.obj = { 'adminware' : obj }
