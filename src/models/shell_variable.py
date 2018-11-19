
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, validates

from database import Base

class ShellVariable(Base):


    key = Column(String)
    value = Column(String)
    batch_id = Column(Integer, ForeignKey('batches.id'))
    batch = relationship("Batch", backref="shell_variables")


    @validates('value')
    def validate_value(self, _, value):
        assert value.isalnum()
        return value
