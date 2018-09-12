
from plumbum import local

__nodeattr = local['nodeattr']['-f', '/var/lib/adminware/genders']

def list():
    groups = __nodeattr('-l').split("\n")
    groups.remove('')
    return groups

def nodes_in(group_name):
    nodes = __nodeattr('-n', group_name).split("\n")
    nodes.remove('')
    return nodes

