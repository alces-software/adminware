
from database import Base, Session, engine

import models.batch

Base.metadata.create_all(engine)

