from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required


from applications import app

# from applications.form_validators import CheckUserDatabase


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy_page():
    # -------------User Packages --------------------#

    from applications.forms import BuyForm
    from applications.models import Brokers
    from applications.database import db

    call_type = "Buy"
    trade_mode = "CNC"
    buy_form = BuyForm()

    # to populate the user's trading codes in buy form.----------------------------------------------------------
    db.session.rollback()
    db.session.begin()
    trading_code = db.session.query(Brokers.trading_code).filter(Brokers.user_id == current_user.id)
    # -----------------------------------------------------------------------------------------------------------

    if request.method == "POST":
        from applications.helpers import SymbolLookup, chk_special

        # --------------------------------- Validating the inputs -----------------------------------------------
        if buy_form.validate_on_submit():
            symbol = (buy_form.symbol.data).upper()
            price = buy_form.price.data
            qty = buy_form.quantity.data
            trading_code = buy_form.code.data
            # type = buy_form.type.data

            # ----- Validates stock symbol ----------------------------
            validate_stock_symbol = SymbolLookup().find_symbol(symbol)

            if validate_stock_symbol:
                from applications.user_database import GetUserData

                data = GetUserData(
                    route="/buy",
                    user_id=current_user.id,
                    trading_code=trading_code,
                    trade_mode=trade_mode,
                    symbol=symbol,
                    call_type=call_type,
                    price=price,
                    qty=qty,
                )
                
                # ------- Logic to get brokerage and taxes----------
                result, message = data.brokerage_and_taxes()
                if not result:
                    flash(message, category="danger")
                    return redirect(url_for("holdings_page", page=1))

                else:
                    # -----Logic to get the balance from the funds table--------
                    result, fund_bal = data.get_balance()
                    if not result:
                        flash(message, category="danger")
                        return render_template("/holdings.html", buy_form=buy_form, trading_code=trading_code)

                    else:
                        # ------Logic to add the buy details to transactions table----------
                        result, message = data.add_transactions()
                        if not result:
                            flash(message, category="danger")
                            return redirect(url_for("holdings_page", page=1))

                        else:
                            # -----Logic to update the funds table---------
                            result, message = data.update_funds()
                            if not result:
                                flash(message, category="danger")
                                return redirect(url_for("holdings_page", page=1))

                            else:
                                # ------ Logic to update the balance in funds table---------

                                result, message = data.update_balance(fund_bal)
                                if not result:
                                    flash(message, category="danger")
                                    return render_template(
                                        "/holdings.html", buy_form=buy_form, trading_code=trading_code
                                    )

                                else:
                                    flash(message, category="success")
                                    return redirect(url_for("holdings_page", page=1))
            else:
                flash("Invalid stock symbol. Check your symbol and try again", category="danger")
                return render_template("/buy.html", buy_form=buy_form, trading_code=trading_code)

        else:
            if "code" in buy_form.errors:
                # print()
                # print("Yes code error")
                # print()
                x = request.form.get("code")
                # print()
                # print(x)
                # print()
            else:
                # print()
                x = request.form.get("code")
                # print(x)
                # print(buy_form.code.data)
                # print()

            flash("Something went wrong with validation! Check all the inputs and try again", category="danger")
            return render_template("/buy.html", buy_form=buy_form, trading_code=trading_code)

    else:
        return render_template("/buy.html", buy_form=buy_form, trading_code=trading_code)
