
from database import Base, Session, engine

from models import job

Base.metadata.create_all(engine)

