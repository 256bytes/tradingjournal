from flask import render_template, request, flash
from flask_login import current_user

from applications import app


@app.route("/get_transaction_details/<trading_code>/<symbol>", methods=["GET", "POST"])
def get_transaction_details_page(trading_code, symbol, holdings):
    trading_code = trading_code
    symbol = symbol

    buy_data = None
    sell_data = None
    from applications.user_database import GetUserData

    data = GetUserData(route="", user_id=current_user.id, trading_code=trading_code, symbol=symbol)

    result, message = data.generate_buy_data()
    if not result:
        flash(message, category="danger")
        return render_template("/home.html")

    else:
        buy_data = message
        result, message = data.generate_sell_data()
        if not result:
            flash(message, category="danger")
            return render_template("/home.html")
        else:
            sell_data = message
            return render_template(
                "/invoice.html", symbol=symbol, trading_code=trading_code, buy_data=buy_data, sell_data=sell_data
            )
