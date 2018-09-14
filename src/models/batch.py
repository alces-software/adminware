
import datetime
import os
from sqlalchemy import Column, String, Integer, DateTime
import yaml

from database import Base

class Batch(Base):
    __tablename__ = 'batches'


    id = Column(Integer, primary_key=True)
    config = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)

    def __name__(self):
        return os.path.basename(os.path.dirname(self.config))

    def help(self):
        default = 'MISSING: Help for {}'.format(self.__name__())
        self.data.setdefault('help', default)
        return self.data['help']

    def command(self):
        n = self.__name__()
        default = 'echo "No command given for: {}"'.format(n)
        self.data.setdefault('command', default)
        return self.data['command']

    def __init__(self, **kwargs):
        self.config = kwargs["config"]
        def __read_data():
            with open(self.config, 'r') as stream:
                return yaml.load(stream) or {}
        self.data = __read_data()
