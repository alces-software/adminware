
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
            session.commit() # Saves the batch to receive and id
            print("Batch: {}".format(self.batch.id))
            for node in ctx.obj['adminware']['nodes']:
                job = Job(node = node, batch = self.batch)
                session.add(job)
                job.run()
                if job.exit_code == 0:
                    symbol = 'Pass'
                else:
                    symbol = 'Failed: {}'.format(job.exit_code)
                print("{}: {}".format(job.node, symbol))
        finally:
            session.commit()
            session.close()

def add_actions(click_group, namespace):
    actions = __glob_actions(namespace)
    for action in actions:
        action.create(click_group)

def __glob_actions(namespace):
    parts = ['/var/lib/adminware/tools', namespace, '*/config.yaml']
    paths = glob.glob(os.path.join(*parts))
    return list(map(lambda x: Action(x), paths))

