import click
import glob

from models.config import Config
from appliance_cli.text import display_table
from os.path import dirname, relpath

def add_commands(appliance):

    @appliance.group(help='View tools')
    def tool():
        pass

    @tool.command(help='List all available tools')
    def list():
        headers = ['Namespace', 'Name', 'Help']
        def table_rows():
            paths = glob.glob('/var/lib/adminware/tools/**/config.yaml', recursive=True)
            # this line was getting mardy so did it manually temporarily
            #configs = list(map(lambda x: Config(x), paths))
            configs = []
            for path in paths:
                config = Config(path)
                configs += [config]
            rows = []
            for config in configs:
                # should be forward compatable with recursive namespaces 
                # calls dirname twice to discard <command_name>/config.yaml
                #   then gets path realtive to tools dir
                namespace = relpath(dirname(dirname(config.path)),'/var/lib/adminware/tools')
                row = [namespace,
                        config.__name__(),
                        config.help(),
                        #add families when they're implemented
                        ]
                rows.append(row)
            return rows
        display_table(headers, table_rows())
        
