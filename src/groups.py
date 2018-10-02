
# all dependancy on nodeattr is to be located in this file
from plumbum import local
from tempfile import NamedTemporaryFile

def list():
    groups = __nodeattr()('-l').split("\n")
    groups.remove('')
    return groups

def nodes_in(group_name):
    nodes = __nodeattr()('-n', group_name).split("\n")
    nodes.remove('')
    return nodes

def expand_nodes(node_list):
    tmp_file = NamedTemporaryFile(dir='/tmp/')
    with open(tmp_file.name, 'w') as f:
        f.write('\n'.join(node_list))
    nodes = __nodeattr(file_path=tmp_file.name)('--expand').split("\n")
    # above split adds trailing empty string in array so
    del nodes[-1]
    return nodes

def __nodeattr(file_path='/var/lib/adminware/genders'):
    return local['nodeattr']['-f', file_path]
