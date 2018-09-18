
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

    def run(self):
        connection = Connection(self.node)
        try:
            connection.open()
        except NoValidConnectionsError as e:
            self.stderr = 'Could not establish ssh connection'
            self.exit_code = -2
            return

        def __set_result(result):
            self.stdout = result.stdout
            self.stderr = result.stderr
            self.exit_code = result.return_code

        # Creates the temporary directory to sync the files to
        result = connection.run('mktemp -d', hide='both')
        if not result:
            __set_result(result)
            return
        temp_dir = result.stdout.rstrip()

        # Copies the files across
        parts = [os.path.dirname(self.batch.config), '*']
        for src_path in glob.glob(os.path.join(*parts)):
            result = connection.put(src_path, temp_dir)
            if not result:
                __set_result(result)
                return

        # Runs the command
        with connection.cd(temp_dir):
            result = connection.run(self.batch.command(), hide='both')
            __set_result(result)

        # Removes the temp directory
        connection.run("rm -rf {}".format(temp_dir))

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

