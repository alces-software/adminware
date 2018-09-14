
import glob
import os
import yaml
import click
import plumbum
from database import Session
from models.batch import Batch

class Action:
    def __init__(self, path):
        self.path = path
        def __read_data():
            with open(self.path, 'r') as stream:
                return yaml.load(stream) or {}
        self.data = __read_data()

    def __name__(self):
        return os.path.basename(os.path.dirname(self.path))

    def create(self, click_group):
        def action_func(ctx, self=self):
            return self.run_command(ctx)
        action_func.__name__ = self.__name__()
        action_func = click.pass_context(action_func)
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click_group.command(help=self.help())(func)

    def help(self):
        default = 'MISSING: Help for {}'.format(self.__name__())
        self.data.setdefault('help', default)
        return self.data['help']

    def command(self):
        n = self.__name__()
        default = 'echo "No command given for: {}"'.format(n)
        self.data.setdefault('command', default)
        return self.data['command']

    def run_command(self, ctx):
        session = Session()
        try:
            batch = Batch(config = self.path)
            session.add(batch)
        finally:
            session.commit()
            session.close()
        for node in ctx.obj['adminware']['nodes']:
            remote = plumbum.machines.SshMachine(node)
            result = self.__run_remote_command(remote)
            remote.close()

    def __run_remote_command(self, remote):
        def __mktemp_d():
            mktemp = remote['mktemp']
            return mktemp('-d').rstrip()

        def __copy_files(dst):
            parts = [os.path.dirname(self.path), '*']
            for src_path in glob.glob(os.path.join(*parts)):
                src = plumbum.local.path(src_path)
                plumbum.path.utils.copy(src, dst)

        def __run_cmd():
            echo = remote['echo']
            bash = remote['bash']
            cmd = echo[self.command()] | bash
            return cmd().rstrip()

        def __rm_rf(path):
            remote['rm']['-rf'](path)

        try:
            temp_dir = __mktemp_d()
            __copy_files(remote.path(temp_dir))
            with remote.cwd(remote.cwd / temp_dir):
                print(__run_cmd())
        finally:
            __rm_rf(temp_dir)

def add_actions(click_group, namespace):
    actions = __glob_actions(namespace)
    for action in actions:
        action.create(click_group)

def __glob_actions(namespace):
    parts = ['/var/lib/adminware/tools', namespace, '*/config.yaml']
    paths = glob.glob(os.path.join(*parts))
    return list(map(lambda x: Action(x), paths))

