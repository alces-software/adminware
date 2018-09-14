
import plumbum

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

    def remote(self):
        return plumbum.machines.SshMachine(self.node)

    def __init__(self, **kwargs):
        self.node = kwargs['node']
        self.batch = kwargs['batch']

