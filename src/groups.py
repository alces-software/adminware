
# all dependancy on nodeattr is to be located in this file
import config

import click
import os.path
from plumbum import local, ProcessExecutionError
from tempfile import NamedTemporaryFile
from re import search

def list_groups():
    groups = __nodeattr(arguments=['-l'])
    return groups

def nodes_in(group_name):
    nodes = __nodeattr(arguments=['-n', group_name])
    return nodes

def compress_nodes(node_list):
    return create_tmp_genders_file(node_list, arguments = ['--compress'])

def expand_nodes(node_list):
    return create_tmp_genders_file(node_list, arguments = ['--expand'])

def create_tmp_genders_file(node_list,  arguments = []):
    # intercept to generate a more useful error message
    #   before invalid nodenames are caught generically in __nodeattr
    for node in node_list:
        if search(r'[^A-z0-9,\[\]]', node):
            raise click.ClickException("""
Invalid nodename {}
May only contain alphanumeric characters and the following symbols: , [ ]
""".strip().format(node))
    # build and parse a genders file of the nodes
    tmp_file = NamedTemporaryFile(dir='/tmp/', prefix='adminware-genders')
    with open(tmp_file.name, 'w') as f:
        f.write('\n'.join(node_list))
    nodes = __nodeattr(file_path=tmp_file.name, arguments=arguments)
    return nodes

def __nodeattr(file_path = config.GENDERS, arguments=[], split_char="\n"):
    if not os.path.isfile(file_path): return []
    try:
        # 'split' below leaves empty string on the end of the array
        #   which is removed
        return local['nodeattr']['-f', file_path](arguments).split(split_char)[:-1]
    except ProcessExecutionError as e:
        raise ClickException(e.stderr.rstrip())
