
from database import Base, Session, engine

from models import job
from models import batch

Base.metadata.create_all(engine)

