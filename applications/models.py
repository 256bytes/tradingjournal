from __future__ import annotations
from flask_login import UserMixin
from alembic import op



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
    script = db.relationship('Transactions', backref='owner_id', lazy=True)
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
    broker_type = db.Column(db.Boolean(), comment="1 for Discount broker and 0 for No Discount Broker")
    equity_delivery = db.Column(db.Float)
    equity_intraday = db.Column(db.Float())
    transaction_chgs = db.Column(db.Float())
    dp_chgs = db.Column(db.Float())

    @property
    def uppercase_convertor(self):
        return self.name
    
    @uppercase_convertor.setter
    def uppercase_convertor(self, value):
        self.name = value.upper()

class Brokers(db.Model):

    __tablename__ = "brokers"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', deferrable=False))
    name = db.Column(db.String(length=45), nullable=False)
    trading_code = db.Column(db.String(length=45), nullable=False)
    broker_type = db.Column(db.Boolean(), comment="1 for Discount broker and 0 for No Discount Broker")
    equity_delivery = db.Column(db.Float(), nullable=False)
    equity_intraday = db.Column(db.Float(), nullable=False)
    transaction_chgs = db.Column(db.Float())
    dp_chgs = db.Column(db.Float())

    @property
    def uppercase_convertor(self):
        return self.trading_code.upper(), self.name.upper()
    
    @uppercase_convertor.setter
    def uppercase_convertor(self, value):
        self.trading_code = value[0].upper()
        self.name = value[1].upper()

    def as_dict(self):
        return {"trading_code": self.trading_code}

class Transactions(db.Model):

    __tablename__ = "transactions"

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE', deferrable=False))
    date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    trade_mode = db.Column(db.String(length=10), comment="Is it Delivery or Intraday" ,nullable=False)
    call = db.Column(db.String(length=10), comment="Buy/Sell", nullable=False)
    script = db.Column(db.String(length=45))
    price = db.Column(db.Float(), nullable=False)
    qty = db.Column(db.Integer(), nullable=False)
    brokerage_per_unit = db.Column(db.Float(), nullable=False)
    total_brokerage = db.Column(db.Float(), nullable=False)
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

    @property
    def uppercase_convertor(self):
        return self.script
    
    @uppercase_convertor.setter
    def uppercase_convertor(self, value):
        self.script = value.upper()

    def as_dict(self):
        return {"script": self.script }

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
    call = db.Column(db.String(length=10), comment="Buy/Sell")
    target = db.Column(db.Float())
    stop_loss = db.Column(db.Float())
    call_validity = db.Column(db.Integer())
    analyst = db.Column(db.String(length=50))
    resource = db.Column(db.Text())
    tgt_sl = db.Column(db.String(length=45), nullable=False, server_default='live', comment="Target/stoploss")


    @property
    def uppercase_convertor(self):
        return self.script
    
    @uppercase_convertor.setter
    def uppercase_convertor(self, value):
        self.script = value.upper()

    def as_dict(self):
        return {"research_symb": self.script}

    def analyst_dict(self):
        return {'analysts': self.analyst}
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
    target_achieved = db.Column(db.Integer())
    stop_loss_triggered = db.Column(db.Integer())
    performance = db.Column(db.Float())



# class Test(db.Model):
#     id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
#     account = db.Column(db.String(length=10))
#     script = db.Column(db.String(length=10))
#     total_qty = db.Column(db.String(length=10))
    

