
# all dependancy on nodeattr is to be located in this file
from plumbum import local, ProcessExecutionError
from tempfile import NamedTemporaryFile
from click import ClickException

def list():
    groups = __nodeattr(arguments=['-l'])
    groups.remove('')
    return groups

def nodes_in(group_name):
    nodes = __nodeattr(arguments=['-n', group_name])
    nodes.remove('')
    return nodes

def expand_nodes(node_list):
    tmp_file = NamedTemporaryFile(dir='/tmp/')
    with open(tmp_file.name, 'w') as f:
        f.write('\n'.join(node_list))
    nodes = __nodeattr(file_path=tmp_file.name, arguments=['--expand'])
    # above split adds trailing empty string in array so
    del nodes[-1]
    return nodes

def __nodeattr(file_path='/var/lib/adminware/genders', arguments=[], split_char="\n"):
    try:
        return local['nodeattr']['-f', file_path](arguments).split(split_char)
    except ProcessExecutionError as e:
        raise ClickException('Unable to process genders file -- {}'.format(e.stderr))
