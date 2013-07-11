from sqlalchemy import Table, Column, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base, metadata


class Account(Base):
    __table__ = Table('accounts', metadata, autoload=True)
    splits = relationship('Split', backref='account')


class Customer(Base):
    __table__ = Table('customers', metadata, autoload=True)


class Transaction(Base):
    __table__ = Table('transactions', metadata, autoload=True)
    splits = relationship('Split', backref='transaction')


class Split(Base):
    __table__ = Table('splits', metadata,
                      Column('tx_guid', VARCHAR, ForeignKey('transactions.guid')),
                      Column('account_guid', VARCHAR, ForeignKey('accounts.guid')),
                      autoload=True)
