from sqlalchemy import Table
from database import Base, metadata


class Account(Base):
    __table__ = Table('accounts', metadata, autoload=True)


class Customer(Base):
    __table__ = Table('customers', metadata, autoload=True)


class Transaction(Base):
    __table__ = Table('transactions', metadata, autoload=True)


class Split(Base):
    __table__ = Table('splits', metadata, autoload=True)
