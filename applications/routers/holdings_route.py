from flask import flash, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func

# -------------User Packages --------------------#
from applications import app


@app.route("/holdings/<int:page>", methods=["GET", "POST"])
@login_required
def holdings_page(page):
    # -------------User Packages --------------------#
    from applications.forms import SellForm, AddForm, AddBonusForm
    from applications.models import Brokers, Transactions
    from applications.database import db
    from applications.helpers import multiple_group
    from applications.user_database import GetUserData

    sell_form = SellForm()
    add_form = AddForm()
    add_bonus = AddBonusForm()

    x = db.session.query(
        Transactions.script, Transactions.trading_code, func.sum(Transactions.qty).label("net_qty")
    ).filter(
        Transactions.user_id == current_user.id
    ).group_by(Transactions.script, Transactions.trading_code).all()


    stock_data = multiple_group(
        current_user.id, (Transactions.script, Transactions.trading_code)
    )  # ------This to get the query with multiple group conditions

    trading_code = db.session.query(Brokers.trading_code).filter(
        Brokers.user_id == current_user.id
    )  # ------To prefill the user's trading codes. This is for sell
    net_investment = (
        db.session.query(func.sum(Transactions.net_total).label("total_investment"))
        .filter(Transactions.user_id == current_user.id, Transactions.trade_mode == "CNC")
        .first()
    )

    # Logic to get the current value of the portfolio
    data = GetUserData(user_id=current_user.id)

    per_page = 10  # Number of items per page
    paginated_holdings = data.get_consolidated_hld_data()
    total_items = len(paginated_holdings)
    total_pages = (total_items + per_page - 1) // per_page
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    holdings = paginated_holdings[start_index:end_index]

    result, message = data.get_invested_value()
    if not result:
        flash(message, category="danger")
        return render_template("home.html")
    else:
        curr_inv_val = message

    result, message = data.get_total_scrips()
    if not result:
        flash(message, category="danger")
        return render_template("home.html")
    else:
        total_scrips = message

    return render_template(
        "holdings.html",
        curr_inv_val=curr_inv_val,
        holdings=holdings,
        sell_form=sell_form,
        add_form=add_form,
        stock_data=stock_data,
        trading_code=trading_code,
        net_investment=net_investment,
        add_bonus=add_bonus,
        page=page,
        total_pages=total_pages,
        total_scrips=total_scrips,
    )
