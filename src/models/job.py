
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

    # The count is not automatically set as the it needs to preform an
    # aggregate query. However the result of the query is stored on the Job
    # object for readability purposes
    count = None

    __connection = None
    __result = None

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

    def connection(self):
        if not self.__connection: self.__connection = Connection(self.node)
        return self.__connection

    class JobTask(asyncio.Task):
        def __init__(self, job, thread_pool = None):
            self.thread_pool = thread_pool
            super().__init__(self.run_async())
            self.job = job
            self.add_job_callback(lambda job: job.connection().close())
            self.add_job_callback(lambda job: job.set_ssh_results())
            self.add_done_callback(type(self).report_results)

        def __getattr__(self, attr):
            return getattr(self.job, attr)

        def add_job_callback(self, func):
            callback = lambda task: func(task.job)
            self.add_done_callback(callback)

        # TODO: Set different "report" callbacks for the three different commands:
        # Possible use inheritance?
        # Exit Code Commands: print_exit_code
        # Report Commands:    print_report
        # Interactive:        noop - do not set the callback
        # This will remove the logic at runtime
        def report_results(self):
            # Do not report interactive jobs
            if self.batch.is_interactive(): return

            # Do not print cancelled Tasks. `self.cancelled()` can't be used
            # as the Task is now in the "done" state
            try: self.exception()
            except concurrent.futures.CancelledError: return
            except Exception as e:
                # TODO: Setup debugging printing at some point
                # print(type(e))
                # print(e)
                pass

            if self.batch.config_model.report:
                click.echo('Node: {}'.format(self.node))
                click.echo(self.stdout)
                click.echo()
            else:
                if self.exit_code == 0:
                    symbol = 'Pass'
                else:
                    symbol = 'Failed: {}'.format(self.exit_code)
                args = [self.id, self.node, symbol]
                click.echo('ID: {}, Node: {}, {}'.format(*args))

        async def __run_thread(self, func, *a):
            def catch_errors(func, *args):
                try: func(*args)
                except: pass
            run = lambda: catch_errors(func, *a)
            coroutine = self._loop.run_in_executor(self.thread_pool, run)
            return await coroutine

        async def run_async(self):
            if self.check_command():
                try: await self.__run_thread(self.connection().open)
                except concurrent.futures.CancelledError as e: raise e

                if self.connection().is_connected:
                    await self.__run_thread(self.run, self.batch)
                else:
                    self.set_ssh_error()

    def task(self, *a, **k): return Job.JobTask(self, *a, **k)

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

    def set_ssh_results(self):
        if self.__result == None: return
        if self.batch.is_interactive():
            self.stdout = 'Interactive Job: STDOUT is unavailable'
            self.stderr = 'Interactive Job: STDERR is unavailable'
            self.exit_code = -3
        else:
            self.stdout = self.__result.stdout
            self.stderr = self.__result.stderr
            self.exit_code = self.__result.return_code

    def run(self, batch):
        def __with_tempdir(func):
            def wrapper(*args):
                result = self.connection().run('mktemp -d', hide='both')
                if result:
                    temp_dir = ('{}'.format(result.stdout)).rstrip()
                    try:
                        result = func(temp_dir, *args)
                    finally:
                        self.connection().run("rm -rf {}".format(temp_dir))
                return result
            return wrapper

        @__with_tempdir
        def __run_command(temp_dir):
            # Copies the files across
            parts = [os.path.dirname(batch.config), '*']
            for src_path in glob.glob(os.path.join(*parts)):
                result = self.connection().put(src_path, temp_dir)
                if not result: return result

            # Runs the command
            with self.connection().cd(temp_dir):
                kwargs = { 'warn' : True }
                if batch.is_interactive():
                    kwargs.update({ 'pty': True })
                else:
                    kwargs.update({ 'hide': 'both' })
                cmd = batch.command()
                if batch.arguments: cmd = cmd + ' ' + quote(batch.arguments)
                return self.connection().run(cmd, **kwargs)
        self.__result = __run_command()

from models.batch import Batch

