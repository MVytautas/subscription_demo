from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    Table,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .meta import Base


association_table = Table('association', Base.metadata,
    Column('subscribers_id', Integer, ForeignKey('subscribers.id')),
    Column('categories_id', Integer, ForeignKey('categories.id'))
)

class Subscriber(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    email = Column(String)
    registered = Column(DateTime(timezone=True), server_default=func.now())
    categories = relationship("Category",
                    secondary=association_table)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(Text) 