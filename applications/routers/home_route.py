from flask import render_template, flash
from flask_login import login_required, current_user
from sqlalchemy import func

# -------------User Packages --------------------#
from applications import app


@app.route("/home", methods=["GET", "POST"])
@login_required
def home_page():
    # -------------User Packages --------------------#
    from ..models import Brokers, Transactions
    from ..database import db
    from ..forms import AddFunds, WithdrawFunds

    brokers = Brokers.query.filter(Brokers.user_id == current_user.id).all()
    add_funds_form = AddFunds()
    withdraw_funds_form = WithdrawFunds()
    investments = []
    funds = []

    # -------------------------------------------------------------------------------
    for brokers_code in brokers:
        # if not funds:
        #     print()
        #     print(type(funds))
        #     print()
        i = (
            db.session.query(func.sum(Transactions.net_total).label("total"))
            .filter(Transactions.user_id == current_user.id, Transactions.trading_code == brokers_code.trading_code)
            .first()
        )
        # f = db.session.query(Funds).filter(Funds.user_id == current_user.id, Funds.trading_code == brokers_code.trading_code).all()
        if i:
            investments.append(i)
            from applications.user_database import GetUserData

            data = GetUserData(user_id=current_user.id, trading_code=brokers_code.trading_code)
            result, available_bal = data.get_balance()
            if not result:
                pass
            else:
                funds.append(available_bal)

        else:
            continue

    return render_template(
        "/home.html",
        funds=funds,
        brokers=brokers,
        investments=investments,
        add_funds_form=add_funds_form,
        withdraw_funds_form=withdraw_funds_form,
    )
