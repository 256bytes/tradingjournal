from flask import flash
from flask_login import UserMixin
from sqlalchemy.orm import validates
from sqlalchemy import text
from alembic import op
import datetime


from applications.database import bcrypt, login_manager
from applications.database import db



@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    hash_password = db.Column(db.String(60), nullable=False)
    last_logged = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now(), nullable=False)
    scripts = db.relationship('Transactions', backref='owner_id', lazy=True)
    brokers = db.relationship('Brokers', backref="user_brokers", lazy=True)
    research = db.relationship('Research', backref="user_research", lazy=True)
    funds = db.relationship('Funds', backref="user_funds", lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.hash_password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.hash_password, attempted_password)

class List_of_brokers(db.Model):

    __tablename__ = "list_of_brokers"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(length=45), nullable=False)
    type = db.Column(db.Boolean())
    equity_delivery = db.Column(db.Float())
    equity_intraday = db.Column(db.Float())
    transaction_chgs = db.Column(db.Float())
    dp_chgs = db.Column(db.Float())

class Brokers(db.Model):

    __tablename__ = "brokers"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', deferrable=False))
    name = db.Column(db.String(length=45), nullable=False)
    trading_code = db.Column(db.String(length=45), nullable=False)
    type = db.Column(db.Boolean())
    equity_delivery = db.Column(db.Float(), nullable=False)
    equity_intraday = db.Column(db.Float(), nullable=False)
    transaction_chgs = db.Column(db.Float())
    dp_chgs = db.Column(db.Float())

    @validates('name', 'trading_code')
    def convert_to_uppper(self, key, value):
        return value.upper()

    def __str__(self) -> str:
        return f"id: {self.id}"

class Transactions(db.Model):

    __tablename__ = "transactions"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', deferrable=False))
    date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    type = db.Column(db.String(length=10), nullable=False)
    call = db.Column(db.String(length=10), nullable=False)
    script = db.Column(db.String(length=45))
    price = db.Column(db.Float(), nullable=False)
    qty = db.Column(db.Integer(), nullable=False)
    brokerage_per_unit = db.Column(db.Float(), nullable=False)
    net_rate_per_unit = db.Column(db.Float(), nullable=False)
    net_total_before_levies = db.Column(db.Float(), nullable=False)
    transaction_chgs = db.Column(db.Float(), nullable=False)
    dp_chgs = db.Column(db.Float(), nullable=False)
    stt = db.Column(db.Float(), nullable=False)
    sebi_turnover_fees = db.Column(db.Float(), nullable=False)
    stamp_duty = db.Column(db.Float(), nullable=False)
    gst = db.Column(db.Float(), nullable=False)
    total_taxes = db.Column(db.Float(), nullable=False)
    net_total = db.Column(db.Float(), nullable=False)
    broker = db.Column(db.String(length=45))
    trading_code = db.Column(db.String(length=45), nullable=False)

class Funds(db.Model):

    __tablename__ = "funds"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', deferrable=False))
    trading_code = db.Column(db.String(length=45), nullable=False)
    pay_in = db.Column(db.Integer(), default=0.00, nullable=False)
    debits = db.Column(db.Float(), default=0.00, nullable=False)
    credits = db.Column(db.Float(), default=0.00, nullable=False)
    pay_out = db.Column(db.Integer(), default=0.00, nullable=False)
    balance = db.Column(db.Float(), default=0.00, nullable=False)

class Research(db.Model):

    __tablename__ = "research"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', deferrable=False))
    date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    script = db.Column(db.String(length=50))
    price = db.Column(db.Float())
    call = db.Column(db.String(length=10))
    stop_loss = db.Column(db.Float())
    target = db.Column(db.Float())
    time_frame = db.Column(db.Integer())
    analyst = db.Column(db.String(length=50))
    performance = db.Column(db.Float())
    resource = db.Column(db.Text())

class Taxes(db.Model):

    __tablename__ = "taxes"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    stt_delivery = db.Column(db.Float(), nullable=False)
    stt_intraday = db.Column(db.Float(), nullable=False)
    gst = db.Column(db.Float(), nullable=False)
    sebi_chgs = db.Column(db.Float(), nullable=False)
    stamp_duty_delivery = db.Column(db.Float(), nullable=False)
    stamp_duty_intraday = db.Column(db.Float(), nullable=False)

class Analysts(db.Model):

    __tablename__ = "analysts"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(100))
    number_of_calls = db.Column(db.Integer())
    stoploss_target = db.Column(db.Integer(), nullable=False, default=0)
    performance = db.Column(db.Float(), nullable=False, default=0)


# class Test(db.Model):
    
#     id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
#     account = db.Column(db.String(length=10))
#     script = db.Column(db.String(length=10))
#     total_qty = db.Column(db.String(length=10))
    

