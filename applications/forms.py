from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, SubmitField,\
                    SelectField, RadioField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from applications.models import Users

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = Users.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    
    def validate_email(self, email_to_check):
        email = Users.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError('Email with same address already exists! Please try a different email')

    username = StringField(label='User Name:', validators=[Length(min=3, max=45), DataRequired()])
    email = StringField(label='Email:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(min=3), DataRequired()])
    confirmation = PasswordField(label='Confirmation Password', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Register')

class AddBrokersForm(FlaskForm):
    name = SelectField(label="Name", choices=[])
    trading_code = StringField(label='Trading Code', validators=[DataRequired()])
    submit = SubmitField(label="Add")
     
class EditBrokerForm(FlaskForm):
    name = StringField(label='Name of the Broker', validators=[DataRequired()])
    trading_code = StringField(label='Trading Code', validators=[DataRequired()])
    equity_delivery = FloatField(label='Brokerage Delivery Chgs:', validators=[DataRequired()])
    equity_intraday = FloatField(label='Brokerage Intraday Chgs:', validators=[DataRequired()])
    update = SubmitField(label='Done')

class LoginFrom(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Log in')

class BuyForm(FlaskForm):
    symbol = StringField(label="Symbol", validators=[DataRequired()])
    quantity = IntegerField(label="Quantity", validators=[DataRequired()])
    price = FloatField(label="Price", validators=[DataRequired()])
    code = StringField(label="Trading Code", validators=[DataRequired()])
    type = RadioField(label="CNC/Intraday", validators=[DataRequired()],
                        choices=[
                                ("CNC", "CNC"),
                                ("Intraday", "Intraday")
                                ])
    submit = SubmitField(label='Buy')

    def to_upper(self, key, value):
        return value.upper()

class SellForm(FlaskForm):
    submit = SubmitField(label='Sell')

class AddForm(FlaskForm):
    submit = SubmitField(label='Add')

class UpdateForm(FlaskForm):
    submit = SubmitField(label='Update')

class SettingForms(FlaskForm):
    submit = SubmitField(label='Close')

class ImportXlsForm(FlaskForm):
    submit = SubmitField(label="Import Holdings")

class ResearchForms(FlaskForm):
    script = StringField(label='Script:', validators=[DataRequired()])
    price = IntegerField(label='Price:', validators=[DataRequired()])
    call = StringField(label='Buy/Sell', validators=[DataRequired()])
    stop_loss = FloatField(label='Stop Loss', validators=[DataRequired()])
    target = FloatField(label='Target', validators=[DataRequired()])
    time_frame = IntegerField(label='Time Frame', validators=[DataRequired()])
    analyst = StringField(label='Analyst Name:', validators=[DataRequired()])
    resource = TextAreaField(label='Resource:')
    submit = SubmitField(label='Add My Research')

class DeleteAnalysis(FlaskForm):
    submit = SubmitField(label='Del')

class AddBonusForm(FlaskForm):
    submit = SubmitField(label="Add Bonus")

class StoplossTargetRadio(FlaskForm):
    
    type = SelectField(label="Sl/Tgt", validators=[DataRequired()],
                        choices=[
                                ("None", "None"),
                                ("SL", "SL"),
                                ("Target", "Target")
                                ], default="None")
    submit = SubmitField(label='Save')
