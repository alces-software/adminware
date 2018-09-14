
from database import Base, Session, engine

from models import batch
from models import job

Base.metadata.create_all(engine)

