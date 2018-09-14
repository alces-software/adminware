
from database import Base, Session, engine

from models import batch

Base.metadata.create_all(engine)

