from applications.database import db, bcrypt
from applications.database import login_manager
from flask_login import UserMixin
from sqlalchemy.orm import validates
import datetime


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.datetime.now())
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    hash_password = db.Column(db.String(60), nullable=False)
    scripts = db.relationship('Transactions', backref='owner_id', lazy=True)
    brokers = db.relationship('Brokers', backref="user_brokers", lazy=True)
    research = db.relationship('Research', backref="user_research", lazy=True)

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

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=45), nullable=False)
    type = db.Column(db.Boolean())
    equity_delivery = db.Column(db.Float())
    equity_intraday = db.Column(db.Float())
    transaction_chgs = db.Column(db.Float())
    dp_chgs = db.Column(db.Float())

class Brokers(db.Model):

    __tablename__ = "brokers"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
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

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    date = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now())
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

# class Holdings(db.Model):

#     __tablename__ = "holdings"

#     id = db.Column(db.Integer(), primary_key=True)
#     date = db.Column(db.DateTime())
#     t_code = db.Column(db.String(length=10), nullable=False)
#     script = db.Column(db.String(length=10), nullable=False)
#     avg_cost = db.Column(db.Float(), nullable=False)
#     qty = db.Column(db.Integer(), nullable=False)
#     invested_amt = db.Column(db.Float(), nullable=False)
#     ltp = db.Column(db.Float(), nullable=False)
#     curr_value = db.Column(db.Float(), nullable=False)
#     profit_loss = db.Column(db.Integer(), nullable=False)

class Research(db.Model):

    __tablename__ = "research"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    date = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now())
    script = db.Column(db.String(length=50))
    price = db.Column(db.Float())
    call = db.Column(db.String(length=10))
    stop_loss = db.Column(db.Float())
    target = db.Column(db.Float())
    time_frame = db.Column(db.Numeric())
    analyst = db.Column(db.String(length=50))
    performance = db.Column(db.Float())
    resource = db.Column(db.Text())

class Taxes(db.Model):

    __tablename__ = "taxes"

    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    stt_delivery = db.Column(db.Float(), nullable=False)
    stt_intraday = db.Column(db.Float(), nullable=False)
    gst = db.Column(db.Float(), nullable=False)
    sebi_chgs = db.Column(db.Float(), nullable=False)
    stamp_duty_delivery = db.Column(db.Float(), nullable=False)
    stamp_duty_intraday = db.Column(db.Float(), nullable=False)

class Analysts(db.Model):

    __tablename__ = "analysts"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    number_of_calls = db.Column(db.Integer())
    stoploss_target = db.Column(db.Integer(), nullable=False, default=0)
    performance = db.Column(db.Float(), nullable=False, default=0)


class Test(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    account = db.Column(db.String(length=10))
    script = db.Column(db.String(length=10))
    total_qty = db.Column(db.String(length=10))
    

