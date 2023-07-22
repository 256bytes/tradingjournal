from flask_wtf import FlaskForm
import requests
from wtforms import StringField, IntegerField, FloatField, PasswordField, SubmitField,\
                    SelectField, RadioField, TextAreaField, DateField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError, NumberRange
from wtforms.widgets.core import DateInput



from applications.models import Users

def no_leading_spaces(FlaskForm, field):
    if field.data.startswith(' '):
        raise ValidationError('Username should not start with a space character')

class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = Users.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    
    def validate_email(self, email_to_check):
        email = Users.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError('Email with same address already exists! Please try a different email')

    username = StringField(label='User Name:', validators=[Length(min=3, max=45), DataRequired(), no_leading_spaces])
    email = StringField(label='Email:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=3), DataRequired()])
    confirmation = PasswordField(label='Confirmation Password:', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Sign up')

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
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Log in')

class BuyForm(FlaskForm):
    symbol = StringField(label="Symbol", validators=[DataRequired()])
    quantity = IntegerField(label="Quantity", validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField(label="Price", validators=[DataRequired(), NumberRange(min=1.0)])
    code = StringField(label="Trading Code", validators=[DataRequired()])
    # type = RadioField(label="Buy/IPO", validators=[DataRequired()],
    #                     choices=[
    #                             ("Buy", "Buy"),
    #                             ("Ipo", "Ipo")
    #                             ])
    submit = SubmitField(label='Buy')

    # def to_upper(self, key, value):
    #     return value.upper()

class SellForm(FlaskForm):
    # symbol = StringField(label="Symbol", validators=[DataRequired()])
    quantity = IntegerField(label="Quantity", validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField(label="Price", validators=[DataRequired(), NumberRange(min=1.0)])
    # code = StringField(label="Trading Code", validators=[DataRequired()], type="hidden")
    # type = RadioField(label="CNC/Intraday", validators=[DataRequired()],
    #                     choices=[
    #                             ("CNC", "CNC"),
    #                             ("Intraday", "Intraday")
    #                             ])
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
    price = FloatField(label='Entry Price:', validators=[DataRequired(), NumberRange(min=1.0)])
    call = SelectField('Buy/Sell', choices=[('buy', 'Buy'), ('sell', 'Sell')],validators=[DataRequired()])
    # call = StringField(label='Buy/Sell', validators=[DataRequired()])
    target = FloatField(label='Target', validators=[DataRequired(), NumberRange(min=1.0)])
    stop_loss = FloatField(label='Stop Loss', validators=[DataRequired(), NumberRange(min=1.0)])
    call_validity = IntegerField(label='Call Validity', validators=[DataRequired(), NumberRange(min=1)])
    analyst = StringField(label='Analyst Name:', validators=[DataRequired()])
    resource = TextAreaField(label='Resource:')
    tgt_sl = StringField(label='tgt_sl:', default='live')
    submit = SubmitField(label='Add My Research')


class DeleteAnalysis(FlaskForm):
    submit = SubmitField(label='Del')

class AddBonusForm(FlaskForm):
    submit = SubmitField(label="Add Bonus")

class StoplossTarget(FlaskForm):
    target_achieved = SelectField('Target Achieved', choices=[('Yes', 'Yes'), ('No', 'No')])
    sl_triggered = SelectField('SL Triggered', choices=[('Yes', 'Yes'), ('No', 'No')])
    submit = SubmitField(label='Save')

class AddFunds(FlaskForm):
    name = StringField(label='Name of the Broker', validators=[DataRequired()])
    trading_code = StringField(label='Trading Code', validators=[DataRequired()])
    add_funds = FloatField(label='Add Funds:', validators=[DataRequired(), NumberRange(min=1.0)])
    submit = SubmitField(label="Add Funds")

class WithdrawFunds(FlaskForm):
    name = StringField(label='Name of the Broker', validators=[DataRequired()])
    trading_code = StringField(label='Trading Code', validators=[DataRequired()])
    withdraw_funds = FloatField(label='Withdraw Funds:', validators=[DataRequired(), NumberRange(min=1.0)])
    submit = SubmitField(label="Pay out")

class DeleteMyAccount(FlaskForm):
    submit = SubmitField(label="Delete My Account")

class PLSearchForm(FlaskForm):
    search_script = StringField(label="Search Symbol",validators=[DataRequired()])
    submit = SubmitField(label="Search")

class AutoCompleteSearchForm(FlaskForm):
    symbols = StringField('symbols', validators=[DataRequired()], render_kw={"placeholder": "Enter Stock Symbol"})
    search_symbol = SubmitField(label='Submit')

    trading_code = StringField('trading_code', validators=[DataRequired()], render_kw={"placeholder": "Enter Trading Code", "onkeydown": "if (event.keyCode == 13) { this.form.submit(); return false; }"})
    search_by_trading_code = SubmitField(label='Submit')

    analyst = StringField('analyst',\
                          validators=[DataRequired()],\
                            render_kw={"placeholder": "Analysts", "onkeydown": "if (event.keyCode == 13) { this.form.submit(); return false; }"})
    search_analyst = SubmitField(label='Submit')

    research_symbols = StringField('research_symbols', validators=[DataRequired()], render_kw={"placeholder": "Enter Stock Symbol"})
    search_research_symbols = SubmitField(label='Submit')

    
