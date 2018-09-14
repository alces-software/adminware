
import plumbum
import os
import glob

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
    batch_id = Column(Integer, ForeignKey('batches.id'))
    batch = relationship("Batch", backref="jobs")

    def run(self):
        def __mktemp_d():
            mktemp = remote['mktemp']
            return mktemp('-d').rstrip()

        def __copy_files(dst):
            parts = [os.path.dirname(self.batch.config), '*']
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

        remote = self.__remote()
        try:
            temp_dir = __mktemp_d()
            __copy_files(remote.path(temp_dir))
            with remote.cwd(remote.cwd / temp_dir):
                print(__run_cmd())
        finally:
            __rm_rf(temp_dir)
            remote.close()

    def __remote(self):
        return plumbum.machines.SshMachine(self.node)

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

