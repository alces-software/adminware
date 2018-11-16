
import config
import inflect as inflect_module
import re

import datetime
from sqlalchemy import create_engine, Column, Integer, orm, DateTime
import sqlalchemy.ext.declarative as declare
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine('sqlite:///{}database.db'.format(config.LEADER))
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Typically the inflect module would be imported as `inflect`, and the
# inflection engine would be called `engine`. However `engine` is already
# taken by the db, so the naming has been tweaked
# https://stackoverflow.com/a/42355087
inflect = inflect_module.engine()

class Base(object):
    @declare.declared_attr
    def __tablename__(cls):
        # Convert the name from CamalCase to snake_case
        # The conversion is based on:
        # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        snake_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return inflect.plural(snake_name)


    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)


    def __init__(self, **kwargs):
        declare.api._declarative_constructor(self, **kwargs)
        self._init_or_load()

    @orm.reconstructor
    def __reconstruct(self):
        self._load()
        self._init_or_load()

    def _load(self): pass
    def _init_or_load(self): pass

Base = declare.declarative_base(cls=Base, constructor = None)

