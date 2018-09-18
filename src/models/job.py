
from fabric import Connection
import os
import glob

from paramiko.ssh_exception import NoValidConnectionsError

import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from models.batch import Batch
from database import Base


class Job(Base):
    __tablename__ = 'jobs'


    id = Column(Integer, primary_key=True)
    node = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    stdout = Column(String)
    stderr = Column(String)
    exit_code = Column(Integer)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    batch = relationship("Batch", backref="jobs")

    def run(self, interactive=False):
        def __with_connection(func):
            def wrapper():
                connection = Connection(self.node)
                try:
                    connection.open()
                except NoValidConnectionsError as e:
                    self.stderr = 'Could not establish ssh connection'
                    self.exit_code = -1
                if connection.is_connected:
                    try:
                        func(connection)
                    finally:
                        connection.close()
            return wrapper

        @__with_connection
        def __runner(connection):
            def __set_result(result):
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
                    kwargs = {}
                    if interactive:
                        kwargs = { 'pty': True }
                    else:
                        kwargs = { 'hide': 'both' }
                    cmd = self.batch.command()
                    result = connection.run(cmd, **kwargs)
                    __set_result(result)
            __run_command()
        __runner()

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

