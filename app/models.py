from app import db


class Account(db.Model):
    __table__ = db.Table('accounts', db.metadata, autoload=True, autoload_with=db.engine)
    splits = db.relationship('Split', backref='account')


class Customer(db.Model):
    __table__ = db.Table('customers', db.metadata, autoload=True, autoload_with=db.engine)


class Transaction(db.Model):
    __table__ = db.Table('transactions', db.metadata, autoload=True, autoload_with=db.engine)
    splits = db.relationship('Split', backref='transaction')


class Split(db.Model):
    __table__ = db.Table('splits', db.metadata,
                      db.Column('tx_guid', db.VARCHAR, db.ForeignKey('transactions.guid')),
                      db.Column('account_guid', db.VARCHAR, db.ForeignKey('accounts.guid')),
                      autoload=True, autoload_with=db.engine)
