from flask import render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func

#-------------User Packages --------------------#
from applications import app

@app.route('/profit_loss', methods=['GET'])
@login_required
def profit_loss_page():

    trade_mode = "CNC"
    #-------------User Packages --------------------#
    from applications.models import Transactions
    from applications.database import db
    from applications.forms import PLSearchForm

    pl_search_form = PLSearchForm()

    # This is to populate the balance column in the profit and loss page.
    net_bal = []
    nb = 0
    for stocks_bought in Transactions.query.filter(Transactions.user_id == current_user.id, Transactions.trade_mode == trade_mode).all():
        results = stocks_bought.__dict__
        nb = nb + results['net_total']
        net_bal.append(nb)

    page = request.args.get('page', 1, int)
    stocks = Transactions.query.filter(Transactions.user_id == current_user.id, Transactions.trade_mode == trade_mode).order_by(Transactions.date.desc()).paginate(page=page, per_page=10)

    # profit_loss = db.session.query(Transactions).filter(Transactions.user_id == current_user.id, Transactions.trade_mode == trade_mode,\
    #                                                     )

    # This bottom line of the statement
    bottom_line_ni = db.session.query(func.sum(Transactions.net_total).label('net_investment')).filter(
                                        Transactions.call == "Buy", Transactions.user_id == current_user.id, Transactions.trade_mode == trade_mode).first()

    bottom_line_tt = db.session.query(func.sum(Transactions.total_taxes).label('total_taxes')).filter(
                                        Transactions.user_id == current_user.id, Transactions.trade_mode == trade_mode).first()

    bottom_line_ss = db.session.query(func.sum(Transactions.net_total).label('net_recievable')).filter(
                                        Transactions.call == "Sell", Transactions.user_id == current_user.id, Transactions.trade_mode == trade_mode).first()
    

    return render_template('profit_loss.html', pl_search_form=pl_search_form, net_bal=net_bal, stocks=stocks, bottom_line_ni=bottom_line_ni, bottom_line_tt=bottom_line_tt, bottom_line_ss=bottom_line_ss)