
import datetime
from sqlalchemy import Column, String, Integer, DateTime

from database import Base

class Job(Base):
    __tablename__ = 'jobs'


    id = Column(Integer, primary_key=True)
    config = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


    def __init__(self, config):
        self.config = config
