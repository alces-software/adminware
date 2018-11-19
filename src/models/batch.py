
from sqlalchemy import Column, String

from database import Base
from models.config import Config
from models.job import Job

class Batch(Base):


    config = Column(String)


    def _init_or_load(self):
        self.config_model = Config(self.config)

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
