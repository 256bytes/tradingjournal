from flask import redirect, url_for, request, flash, render_template
from flask_login import current_user, login_required
from sqlalchemy import update

# -------------User Packages --------------------#
from applications import app
from applications.forms import WithdrawFunds


@app.route("/withdraw_funds", methods=["GET", "POST"])
@login_required
def withdraw_funds():
    withdraw_funds_form = WithdrawFunds()
    if request.method == "POST":
        if withdraw_funds_form.validate_on_submit():
            from applications.validate_database import ValidateUserDatabase

            trading_code = withdraw_funds_form.trading_code.data

            # -------Checking for valid trading code of the user.-------------------------
            user_broker_data = ValidateUserDatabase()
            result, message = user_broker_data.validate_trader_code(current_user.id, trading_code)
            if not result:
                flash(message, category="danger")
                return render_template("home.html", withdraw_funds_form=withdraw_funds_form)

            else:
                # ------Checking the available balance with the account.--------------------
                withdrawal_amt = withdraw_funds_form.withdraw_funds.data

                from applications.user_database import GetUserData

                data = GetUserData(user_id=current_user.id, trading_code=trading_code)
                result, fund_bal = data.get_balance()

                if not result:
                    flash(message, category="danger")
                    return render_template("home.html", withdraw_funds_form=withdraw_funds_form)

                else:
                    if withdrawal_amt > fund_bal:
                        flash(f"insufficient fund in {trading_code} account.", category="danger")
                        return render_template("home.html", withdraw_funds_form=withdraw_funds_form)

                    else:
                        # ------------Logic to withdraw the amount-----------------------------
                        result, message = data.withdraw_fund(withdrawal_amt)
                        if not result:
                            flash(message, category="danger")
                            return render_template("home.html", withdraw_funds_form=withdraw_funds_form)

                        else:
                            # -------Logic to update the balance after withdrawal------------------
                            result, message = data.update_balance(fund_bal)
                            if not result:
                                flash(message, category="danger")
                                return render_template("home.html", withdraw_funds_form=withdraw_funds_form)
                            else:
                                flash(message, category="success")
                                return redirect(url_for("home_page"))
        else:
            flash(f"something went wrong with validation", category="danger")
            return render_template("home.html", withdraw_funds_form=withdraw_funds_form)
    else:
        return render_template("home.html", withdraw_funds_form=withdraw_funds_form)
