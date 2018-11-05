
from fabric import Connection
import os
import glob

import datetime
from shlex import quote
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

import threading

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

    kill_connection_event = threading.Event()

    def run(self):
        def __check_command(func):
            def wrapper():
                if self.batch.command_exists():
                    func()
                else:
                    self.stderr = 'Incorrectly configured command'
                    self.exit_code = -2
            return wrapper

        def __with_connection(func):
            def wrapper():
                connection = Connection(self.node)
                def run_function():
                    try: func(connection)
                    # Do not pass on errors, they should already be handled
                    except: pass
                    # Flag the job as finished
                    finally: self.kill_connection_event.set()

                try:
                    connection.open()
                except:
                    self.stderr = 'Could not establish ssh connection'
                    self.exit_code = -1
                if connection.is_connected:
                    try:
                        worker = threading.Thread(target = run_function)
                        worker.start()
                        self.kill_connection_event.wait()
                        worker.join(1) # Do not block as it might be interrupted
                    finally:
                        connection.close()
            return wrapper

        @__check_command
        @__with_connection
        def __runner(connection):
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
                    result = connection.run('mktemp -d', hide='both')
                    if result:
                        temp_dir = result.stdout.rstrip()
                        try:
                            func(temp_dir, *args)
                        finally:
                            connection.run("rm -rf {}".format(temp_dir))
                    else:
                        __set_result(result)
                return wrapper

            @__with_tempdir
            def __run_command(temp_dir):
                # Copies the files across
                parts = [os.path.dirname(self.batch.config), '*']
                for src_path in glob.glob(os.path.join(*parts)):
                    result = connection.put(src_path, temp_dir)
                    if not result:
                        __set_result(result)
                        return

                # Runs the command
                with connection.cd(temp_dir):
                    kwargs = { 'warn' : True }
                    if self.batch.is_interactive():
                        kwargs.update({ 'pty': True })
                    else:
                        kwargs.update({ 'hide': 'both' })
                    cmd = self.batch.command()
                    if self.batch.arguments: cmd = cmd + ' ' + quote(self.batch.arguments)
                    result = connection.run(cmd, **kwargs)
                    __set_result(result)
            __run_command()
        __runner()

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

from models.batch import Batch

