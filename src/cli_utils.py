
import groups

def set_nodes_context(ctx, **kwargs):
    obj = { 'nodes' : [] }
    if kwargs['node']: obj['nodes'].append(kwargs['node'])
    if kwargs['group']:
        obj['nodes'].extend(groups.nodes_in(kwargs['group']))
    ctx.obj = { 'adminware' : obj }
