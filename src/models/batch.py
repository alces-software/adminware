
import datetime
from sqlalchemy import Column, String, Integer, DateTime, orm

from database import Base
from models.config import Config
from models.job import Job

class Batch(Base):


    config = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


    def __name__(self):
        return self.config_model.__name__()

    def name(self):
        return self.config_model.name()

    def help(self):
        return self.config_model.help()

    def command(self):
        return self.config_model.command()

    def command_exists(self):
        return self.config_model.command_exists()

    def is_interactive(self):
        return self.config_model.interactive()

    def build_jobs(self, *nodes):
        return list(map(lambda n: Job(node = n, batch = self), nodes))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__init_or_load__()

    @orm.reconstructor
    def __load__(self):
        self.__init_or_load__()

    def __init_or_load__(self):
        self.config_model = Config(self.config)
