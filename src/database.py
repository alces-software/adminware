
import config

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///{}database.db'.format(config.LEADER))
Session = sessionmaker(bind=engine)

Base = declarative_base()
