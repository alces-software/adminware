
import config
import inflect as inflect_module

from sqlalchemy import create_engine, Column, Integer, orm
import sqlalchemy.ext.declarative as declare
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

engine = create_engine('sqlite:///{}database.db'.format(config.LEADER))
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Typically inflect would the module name and engine dose the inflection
# However `engine` is already taken by the db, so the naming has been tweaked
# https://stackoverflow.com/a/42355087
inflect = inflect_module.engine()

class Base(object):
    @declare.declared_attr
    def __tablename__(cls):
        return inflect.plural(cls.__name__.lower())

    id = Column(Integer, primary_key=True)

Base = declare.declarative_base(cls=Base)

class InitOrLoadModel(object):
    def __init__(self, *a, **kwargs):
        super().__init__(*a, **kwargs)
        self.__init_or_load__()

    @orm.reconstructor
    def __load__(self): self.__init_or_load__()
    def __init_or_load__(self): pass

