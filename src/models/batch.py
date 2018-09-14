
import datetime
from sqlalchemy import Column, String, Integer, DateTime

from database import Base

class Batch(Base):
    __tablename__ = 'batches'


    id = Column(Integer, primary_key=True)
    config = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


    def __init__(self, **kwargs):
        self.config = kwargs["config"]
