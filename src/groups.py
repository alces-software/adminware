
# all dependancy on nodeattr is to be located in this file
import config

import click
import os.path
from plumbum import local, ProcessExecutionError
from tempfile import NamedTemporaryFile
from re import search

def list_():
    return _nodeattr(arguments=['-l'])

def nodes_in(group_name):
    return _nodeattr(arguments=['-n', group_name])

def compress_nodes(node_list):
    return _create_tmp_genders_file(node_list, arguments = ['--compress'])[0]

def expand_nodes(node_list):
    return _create_tmp_genders_file(node_list, arguments = ['--expand'])

def _create_tmp_genders_file(node_list,  arguments = []):
    # intercept to generate a more useful error message
    #   before invalid nodenames are caught generically in _nodeattr
    for node in node_list:
        if search(r'[^A-z0-9,\[\]]', node):
            raise click.ClickException("""
Invalid node '{}'
May only contain alphanumeric characters and the following symbols: , [ ]
""".strip().format(node))
    # build and parse a genders file of the nodes
    tmp_file = NamedTemporaryFile(dir='/tmp/', prefix='adminware-genders')
    with open(tmp_file.name, 'w') as f:
        f.write('\n'.join(node_list))
    nodes = _nodeattr(file_path = tmp_file.name, arguments = arguments)
    # above split adds trailing empty string in array so
    del nodes[-1]
    return nodes

def _nodeattr(file_path = config.GENDERS, arguments=[], split_char="\n"):
    if not os.path.isfile(file_path): return []
    try:
        # 'split' below leaves empty string on the end of the array
        #   which is removed
        return local['nodeattr']['-f', file_path](arguments).split(split_char)[:-1]
    except ProcessExecutionError as e:
        raise ClickException(e.stderr.rstrip())
