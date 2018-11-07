
from fabric import Connection
import os
import glob

import click

import datetime
from shlex import quote
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

import asyncio
import concurrent

class Job(Base):
    __tablename__ = 'jobs'


    id = Column(Integer, primary_key=True)
    node = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    stdout = Column(String)
    stderr = Column(String, default = '''
Internal Error: Abandoned Job Error

This job was added to the queue before being abandoned. No further results are
available. Please see documentation for possible causes
'''.strip())
    exit_code = Column(Integer, default=-4)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    batch = relationship("Batch", backref="jobs")

    __connection = None

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

    def connection(self):
        if not self.__connection: self.__connection = Connection(self.node)
        return self.__connection

    class JobTask(asyncio.Task):
        def __init__(self, job, *a, **k):
            super().__init__(self.run_async(), *a, **k)
            self.job = job
            self.add_job_callback(lambda job: job.connection().close())
            self.add_done_callback(type(self).report_results)

        def __getattr__(self, attr):
            return getattr(self.job, attr)

        def add_job_callback(self, func):
            callback = lambda task: func(task.job)
            self.add_done_callback(callback)

        def report_results(self):
            if self.exit_code == 0:
                symbol = 'Pass'
            else:
                symbol = 'Failed: {}'.format(self.exit_code)
            click.echo('ID: {}, Node: {}, {}'.format(self.id, self.node, symbol))

        async def __run_thread(self, func, *a):
            return await self._loop.run_in_executor(None, func, *a)

        async def run_async(self):
            if self.check_command():
                try: await self.__run_thread(self.connection().open)
                except concurrent.futures.CancelledError: pass
                except: self.set_ssh_error()

                if self.connection().is_connected:
                    await self.__run_thread(self.run)

    def task(self): return Job.JobTask(self)

    def check_command(self):
        if self.batch.command_exists(): return True
        else:
            self.stdout = ''
            self.stderr = 'Incorrectly configured command'
            self.exit_code = -2

    def set_ssh_error(self):
        self.stdout = ''
        self.stderr = 'Could not establish ssh connection'
        self.exit_code = -1

    def run(self):
        def __set_result(result):
            if self.batch.is_interactive():
                self.stdout = 'Interactive Job: STDOUT is unavailable'
                self.stderr = 'Interactive Job: STDERR is unavailable'
                self.exit_code = -3
            else:
                self.stdout = result.stdout
                self.stderr = result.stderr
                self.exit_code = result.return_code

        def __with_tempdir(func):
            def wrapper(*args):
                result = self.connection().run('mktemp -d', hide='both')
                if result:
                    temp_dir = result.stdout.rstrip()
                    try:
                        func(temp_dir, *args)
                    finally:
                        self.connection().run("rm -rf {}".format(temp_dir))
                else:
                    __set_result(result)
            return wrapper

        @__with_tempdir
        def __run_command(temp_dir):
            # Copies the files across
            parts = [os.path.dirname(self.batch.config), '*']
            for src_path in glob.glob(os.path.join(*parts)):
                result = self.connection().put(src_path, temp_dir)
                if not result:
                    __set_result(result)
                    return

            # Runs the command
            with self.connection().cd(temp_dir):
                kwargs = { 'warn' : True }
                if self.batch.is_interactive():
                    kwargs.update({ 'pty': True })
                else:
                    kwargs.update({ 'hide': 'both' })
                cmd = self.batch.command()
                if self.batch.arguments: cmd = cmd + ' ' + quote(self.batch.arguments)
                result = self.connection().run(cmd, **kwargs)
                __set_result(result)
        __run_command()

from models.batch import Batch

