from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

#-------------User Packages --------------------#
from applications import app
from ..models import Brokers, Transactions, Funds
from ..database import db
from ..forms import AddFunds, WithdrawFunds


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home_page():
    
    brokers = Brokers.query.filter(Brokers.user_id == current_user.id).all()
    add_funds_form = AddFunds()
    withdraw_funds_form = WithdrawFunds()
    investments = []
    funds = []
    for brokers_code in brokers:
        i = db.session.query(func.sum(Transactions.net_total).label("total")).filter(Transactions.user_id == current_user.id, Transactions.trading_code == brokers_code.trading_code).first()
        f = db.session.query(Funds).filter(Funds.user_id == current_user.id, Funds.trading_code == brokers_code.trading_code).all()
        if i and f:
            # This block gets the pay in, pay out, debit and credit to calculate the net balance.
            # So that it can displayed in dashboard.
            f_in = db.session.query(func.sum(Funds.pay_in).label('pay_in_funds')).filter(Funds.user_id == current_user.id, Funds.trading_code == brokers_code.trading_code).first()
            deb = db.session.query(func.sum(Funds.debits).label('debit')).filter(Funds.user_id == current_user.id, Funds.trading_code == brokers_code.trading_code).first()
            cred = db.session.query(func.sum(Funds.credits).label('credit')).filter(Funds.user_id == current_user.id, Funds.trading_code == brokers_code.trading_code).first()
            f_out = db.session.query(func.sum(Funds.pay_out).label('pay_out_funds')).filter(Funds.user_id == current_user.id, Funds.trading_code == brokers_code.trading_code).first()
            net_bal = ((float(f_in.pay_in_funds) + float(cred.credit)) - (float(deb.debit) + float(f_out.pay_out_funds)))
            
            investments.append(i)
            funds.append(net_bal)

        else:
            return render_template('/home.html', brokers=brokers, investments=investments, add_funds_form=add_funds_form, funds=funds, withdraw_funds_form=withdraw_funds_form)
    
    return render_template('/home.html', brokers=brokers, investments=investments, add_funds_form=add_funds_form, funds=funds, withdraw_funds_form=withdraw_funds_form)
        


    