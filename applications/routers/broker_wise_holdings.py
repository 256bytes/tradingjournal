
"""
This route ensures to sort the holdings by the user's trading_account:
"""
from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from flask_paginate import Pagination, get_page_parameter

from applications import app
from applications.database import db
from applications.models import Transactions
from applications.forms import AutoCompleteSearchForm, SellForm, AddForm, AddBonusForm
from applications.user_database import GetUserData
from applications.helpers import multiple_group


@app.route('/broker_wise_holdings/<int:page>', methods=["GET", "POST"])
@login_required
def broker_wise_holding_page(page):

        caller = "broker_wise_holding_page"
        # Pass the forms to modals
        sell_form = SellForm()
        add_form = AddForm()
        add_bonus = AddBonusForm()
        # Get the trading_code from the layout form
        
        stock_data = multiple_group(
        current_user.id, (Transactions.script, Transactions.trading_code)
    ) 
        trading_code = request.args.get('trading_code')
        # print()
        # print(f"this is from broker wise py: {trading_code}")
        # print()
        acs_form = AutoCompleteSearchForm()

        # Broker name and trading code is passed to html page, so that it can be rendered over the table.
        broker_name = db.session.query(Transactions.broker).\
        filter(Transactions.user_id == current_user.id,\
                Transactions.trading_code == trading_code).\
                first()
        
        # Get the Net Investment Broker wise
        net_investment = db.session.query(func.sum(
                Transactions.net_total).label("total_investment")).\
                filter(
                Transactions.user_id == current_user.id,\
                Transactions.trading_code == trading_code,\
                Transactions.trade_mode == "CNC"
                ).first()

        
        # Logic to get the current value of the portfolio
        data = GetUserData(user_id = current_user.id, trading_code=trading_code)
        
        per_page = 10  # Number of items per page
        paginated_holdings = data.get_consolidated_hld_data()
        total_items = len(paginated_holdings)
        total_pages = (total_items + per_page - 1) // per_page
        start_index = (page - 1) * per_page
        end_index = start_index + per_page

        holdings = paginated_holdings[start_index:end_index]

        result, message = data.get_invested_value()
        if not result:
                flash(message, category='danger')
                return render_template('home.html')
        else:
                curr_inv_val = message

        result, message = data.get_total_scrips()

        if not result:
                flash(message, category="danger")
                return render_template("home.html")
        else:
                total_scrips = message

        return render_template('/broker_wise_holdings.html',
                               acs_form=acs_form,
                               curr_inv_val=curr_inv_val,
                               holdings=holdings,
                               broker_name=broker_name,
                               trading_code=trading_code,
                               net_investment=net_investment,
                               sell_form=sell_form,
                                add_form=add_form,
                                add_bonus=add_bonus,
                               page=page,
                                total_pages=total_pages,
                                stock_data=stock_data,
                                caller=caller,
                                total_scrips=total_scrips
                                )


