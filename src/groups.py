
# all dependancy on nodeattr is to be located in this file
import config
from models.config import Config
from appliance_cli.command_generation import generate_commands

from plumbum import local, ProcessExecutionError
from tempfile import NamedTemporaryFile
from click import ClickException
from re import search

def group_commands(root_command, **kwargs):
    def __group_commands(callback):
        groups_hash = __hashify_all_groups(**kwargs)
        generate_commands(root_command, groups_hash, callback)
    return __group_commands

# Generates a similar hash to Config hasify funcs - for node groups
#   {
#       groupX: **<node>,
#       ...
#   }
def __hashify_all_groups(command = {}):
    combined_hash = {}
    for group in list_groups():
        group_hash = combined_hash.setdefault(group, {})
        Config._Config__copy_values(command, group_hash, group)
    return combined_hash

def list_groups():
    groups = __nodeattr(arguments=['-l'])
    groups.remove('')
    return groups

def nodes_in(group_name):
    nodes = __nodeattr(arguments=['-n', group_name])
    nodes.remove('')
    return nodes

def expand_nodes(node_list):
    # intercept to generate a more useful error message
    #   before invalid nodenames are caught generically in __nodeattr
    for node in node_list:
        if search(r'[^A-z0-9,\[\]]',node):
            raise ClickException(
                    "Invalid nodename {} - may only contain alphanumerics, ',', '[' and ']'"
                    .format(node))

    # build and parse a genders file of the nodes
    tmp_file = NamedTemporaryFile(dir='/tmp/', prefix='adminware-genders')
    with open(tmp_file.name, 'w') as f:
        f.write('\n'.join(node_list))
    nodes = __nodeattr(file_path=tmp_file.name, arguments=['--expand'])
    # above split adds trailing empty string in array so
    del nodes[-1]
    return nodes

def __nodeattr(file_path='{}genders'.format(config.LEADER), arguments=[], split_char="\n"):
    try:
        return local['nodeattr']['-f', file_path](arguments).split(split_char)
    except ProcessExecutionError as e:
        raise ClickException(e.stderr.rstrip())
