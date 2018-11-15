
import datetime
from sqlalchemy import Column, String, Integer, DateTime

from database import Base, InitOrLoadModel
from models.config import Config
from models.job import Job

class Batch(InitOrLoadModel, Base):


    config = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


    def __init_or_load__(self):
        self.config_model = Config(self.config)

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
