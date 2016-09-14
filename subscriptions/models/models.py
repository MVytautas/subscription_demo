import bcrypt
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

class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    login = Column(Text)
    password = Column(Text)


class Subscriber(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    registered = Column(DateTime(timezone=True), server_default=func.now())
    categories = relationship("Category",
                              secondary=association_table)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(Text)

class User(Base):
    """ The SQLAlchemy declarative model class for a User object. """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    role = Column(Text, nullable=False)

    password_hash = Column(Text)

    def set_password(self, pw):
        pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password_hash = pwhash.decode('utf8')

    def check_password(self, pw):
        if self.password_hash is not None:
            expected_hash = self.password_hash.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False