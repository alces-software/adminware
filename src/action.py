
import glob
import click
import plumbum
import os
from database import Session
from models.batch import Batch
from models.job import Job

class Action:
    def __init__(self, path):
        self.path = path
        self.batch = Batch(config = self.path)

    def create(self, click_group):
        def action_func(ctx, self=self):
            return self.run_command(ctx)
        action_func.__name__ = self.batch.__name__()
        action_func = click.pass_context(action_func)
        action_func = self.__click_command(action_func, click_group)

    def __click_command(self, func, click_group):
        return click_group.command(help=self.batch.help())(func)

    def run_command(self, ctx):
        session = Session()
        try:
            session.add(self.batch)
            for node in ctx.obj['adminware']['nodes']:
                job = Job(node = node, batch = self.batch)
                session.add(job)
                remote = job.remote()
                result = self.__run_remote_command(remote)
                remote.close()
        finally:
            session.commit()
            session.close()

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
            cmd = echo[self.batch.command()] | bash
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

