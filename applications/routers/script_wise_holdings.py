from flask import render_template, request
from flask_login import current_user
import inspect

from applications import app
from applications.database import db
from applications.models import Transactions
from applications.forms import AutoCompleteSearchForm, SellForm, AddForm, AddBonusForm
from applications.helpers import multiple_group
from applications.user_database import GetUserData

@app.route("/script_wise_holdings/<int:page>", methods=["GET", "POST"])
def script_wise_holdings_page(page):
    caller = request.args.get("caller")
    caller_trading_code = request.args.get("trading_code")
    analyst = request.args.get("analyst")
    sell_form = SellForm()
    add_form = AddForm()
    add_bonus = AddBonusForm()

    acs_form = AutoCompleteSearchForm()

    if request.method == "POST":
        symbol = acs_form.symbols.data
        current_page = page
        print()
        print(f"current page from post: {page}")
        print()
    else:
        symbol = request.args.get("data")
        current_page = page

        print()
        print(f"current page from get: {current_page}")
        print()
    stock_data = multiple_group(
        current_user.id, (Transactions.script, Transactions.trading_code)
    )  # ------This to get the query with multiple group conditions

    per_page = 10  # Number of items per page
    data = GetUserData(user_id = current_user.id, symbol = symbol)
    paginated_holdings = data.get_consolidated_hld_data()
    total_items = len(paginated_holdings)
    total_pages = (total_items + per_page - 1) // per_page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    holdings = paginated_holdings[start_index:end_index]

    # data = (
    #     db.session.query(
    #         Transactions,
    #         func.sum(Transactions.qty).label("net_qty"),
    #         func.sum(Transactions.net_total).label("total_investments"),
    #     )
    #     .filter(Transactions.user_id == current_user.id, Transactions.script == symbol)
    #     .group_by(Transactions.trading_code, Transactions.script)
    #     .all()
    # )
    return render_template(
        "/script_wise_holdings.html",
        holdings=holdings,
        stock_data=stock_data,
        sell_form=sell_form,
        add_form=add_form,
        add_bonus=add_bonus,
        symbol=symbol,
        page=page,
        total_pages=total_pages,
        current_page=current_page,
        caller=caller,
        caller_trading_code=caller_trading_code,
        analyst=analyst
    )
