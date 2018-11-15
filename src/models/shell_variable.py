
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class ShellVariable(Base):


    key = Column(String)
    value = Column(String)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    batch = relationship("Batch", backref="shell_variables")
