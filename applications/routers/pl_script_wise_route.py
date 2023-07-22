from flask import render_template, request
from flask_login import current_user
from sqlalchemy import and_, or_, func, distinct

from applications import app


@app.route("/pl_script_wise/<int:page>", methods=["GET"])
def pl_script_wise_page(page):
    script_wise_data = []
    net_pandl = []
    keys = ["date", "user_id", "script", "trading_code", "call", "price", "qty", "net_total", "net_pl"]
    from applications.models import Transactions, db
    from applications.user_database import GetUserData

    data = GetUserData(user_id = current_user.id)
    # holdings = data.get_script_wise_pl()

    per_page = 10  # Number of items per page
    paginated_holdings, pl = data.get_script_wise_pl() # get_script_wise_pl returns 2 arguments. ignore the second
    total_items = len(paginated_holdings)
    total_pages = (total_items + per_page - 1) // per_page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    holdings = paginated_holdings[start_index:end_index]

    hld, total_gain_loss = data.get_script_wise_pl() # get_script_wise_pl returns 2 arguments. ignore the first

    # script_wise_pl = (
    #     db.session.query(
    #         Transactions.user_id,
    #         Transactions.script,
    #         Transactions.trading_code,
    #         func.sum(Transactions.net_total).label("net_profit_loss"),
    #     )
    #     .filter(and_(Transactions.user_id == current_user.id, Transactions.call.in_(["Buy", "Sell"])))
    #     .group_by(Transactions.script, Transactions.trading_code)
    #     .having(or_(func.count(distinct(Transactions.call)) == 2))
    #     .all()
    # )
    # for x in script_wise_pl:

    #     all_data = (
    #         db.session.query(Transactions)
    #         .filter(
    #             Transactions.user_id == current_user.id, Transactions.script == x[1], Transactions.trading_code == x[2]
    #         )
    #         .all()
    #     )

    #     for a in all_data:
    #         script_wise_data.append(a)

    return render_template("/pl_script_wise.html",holdings=holdings, page=page,
                                total_pages=total_pages, total_gain_loss=total_gain_loss)
