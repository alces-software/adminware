
from fabric import Connection
import plumbum
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

        # Code below this line uses the original plumbum ssh library

        def __with_remote(func):
            def wrapper(*args, **kwargs):
                remote = None
                remote = plumbum.machines.SshMachine(self.node)
                if remote: func(remote, *args, **kwargs)
            return wrapper

        def __mktemp_d(remote):
            pass

        def __copy_files(remote, dst):
            pass

        def __run_cmd(remote):
            echo = remote['echo']
            bash = remote['bash']
            cmd = echo[self.batch.command()] | bash
            return cmd.run()

        def __rm_rf(remote, path):
            remote['rm']['-rf'](path)

        @__with_remote
        def __run(remote):
            try:
                __copy_files(remote, remote.path(temp_dir))
                with remote.cwd(remote.cwd / temp_dir):
                    results = __run_cmd(remote)
                    self.exit_code = results[0]
                    self.stdout = results[1]
                    self.stderr = results[2]
            except Exception as err:
                self.stderr = str(err)
                self.exit_code = -1
            finally:
                __rm_rf(remote, temp_dir)
                remote.close()
        __run()

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

