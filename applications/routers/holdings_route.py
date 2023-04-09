from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from sqlalchemy import func


from applications import app
from applications.forms import SellForm, AddForm, AddBonusForm
from applications.models import Brokers, Transactions
from applications.database import db
from applications.helpers import multiple_group


@app.route('/holdings', methods=['GET', 'POST'])
@login_required
def holdings_page():
    

    sell_form = SellForm()
    add_form = AddForm()
    add_bonus = AddBonusForm()
  
    stock_data = multiple_group(current_user.id, (Transactions.script, Transactions.trading_code)) #------This to get the query with multiple group conditions
    t_code = db.session.query(Brokers.trading_code).filter(Brokers.user_id == current_user.id) #------To prefill the user's trading codes. This is for sell
    net_investment = db.session.query(func.sum(Transactions.net_total).label('total_investment')).filter(Transactions.user_id == current_user.id, Transactions.type == "CNC").first()
    
    
    page = request.args.get('page', 1, int)
    holdings = db.session.query(Transactions.script, func.sum(Transactions.qty).label('shares'), func.sum(Transactions.net_total).label('total_investments')).\
                            filter(Transactions.user_id == current_user.id, Transactions.type == 'CNC').\
                                group_by(Transactions.script).paginate(page=page, per_page=10)

    return render_template('holdings.html', holdings=holdings, sell_form=sell_form, add_form=add_form,\
                                                    stock_data=stock_data, t_code=t_code, net_investment=net_investment, add_bonus=add_bonus)