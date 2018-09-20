
import datetime
from sqlalchemy import Column, String, Integer, DateTime, orm

from database import Base
from models.config import Config

class Batch(Base):
    __tablename__ = 'batches'


    id = Column(Integer, primary_key=True)
    config = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


    def __name__(self):
        return self.config_model.__name__()

    def help(self):
        return self.config_model.help()

    def command(self):
        return self.config_model.command()

    def __init__(self, **kwargs):
        self.config = kwargs['config']
        self.__init_or_load()

    @orm.reconstructor
    def __load(self):
        self.__init_or_load()

    def __init_or_load(self):
        self.config_model = Config(self.config)
