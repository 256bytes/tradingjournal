from flask import flash, redirect, url_for, request, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

# -------------User Packages --------------------#
from applications import app
from applications.forms import SellForm
from applications.database import db
from applications.calc_taxes.get_taxes import CalculateBrokerageAndTaxes


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell_page():
    call_type = "Sell"
    trade_mode = "CNC"
    sell_form = SellForm()
    if request.method == "POST":
        # --------------------------------- Validating the inputs -----------------------------------------------
        if sell_form.validate_on_submit():
            symbol = request.form.get("script").upper()
            trading_code = request.form.get("code")
            qty = sell_form.quantity.data
            price = sell_form.price.data

            from applications.user_database import GetUserData

            data = GetUserData(
                route="/sell",
                user_id=current_user.id,
                trading_code=trading_code,
                trade_mode=trade_mode,
                symbol=symbol,
                call_type=call_type,
                price=price,
                qty=qty,
            )
            result, message = data.validate_qty_to_sell(qty)
            if not result:
                flash(message, category="danger")
                return render_template("/home.html", sell_form=sell_form)
            else:
                result, message = data.brokerage_and_taxes()
                if not result:
                    flash(message, category="danger")
                    return render_template("/home.html", sell_form=sell_form)

                else:
                    result, fund_bal = data.get_balance()
                    if not result:
                        flash(message, category="danger")
                        return render_template("/home.html", sell_form=sell_form)

                    else:
                        result, message = data.add_transactions()
                        if not result:
                            flash(message, category="danger")
                            return render_template("/home.html", sell_form=sell_form)

                        else:
                            result, message = data.update_funds()
                            if not result:
                                flash(message, category="danger")
                                return redirect(url_for("holdings_page"))

                            else:
                                result, message = data.update_balance(fund_bal)
                                if not result:
                                    flash(message, category="danger")
                                    return render_template("/home.html", sell_form=sell_form)

                                else:
                                    flash(message, category="success")
                                    return render_template("/home.html", sell_form=sell_form)
        else:
            flash("Something went wrong with validation! Check all the inputs and try again", category="danger")
            return render_template("/home.html", sell_form=sell_form)
    else:
        return render_template("/home.html", sell_form=sell_form)
