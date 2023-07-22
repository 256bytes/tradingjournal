from flask import redirect, url_for, request, flash, render_template
from flask_login import current_user, login_required
from sqlalchemy import update

# -------------User Packages --------------------#
from applications import app


@app.route("/add_funds", methods=["GET", "POST"])
@login_required
def add_funds():
    from applications.forms import AddFunds

    add_funds_forms = AddFunds()

    if request.method == "POST":
        if add_funds_forms.validate_on_submit():
            # -------------User Packages --------------------#
            from applications.user_database import GetUserData

            # broker_name = add_funds_forms.name.data
            trading_code = add_funds_forms.trading_code.data
            add_fund = add_funds_forms.add_funds.data

            data = GetUserData(user_id=current_user.id, trading_code=trading_code)
            result, fund_bal = data.get_balance()
            # data.update_balance(fund_bal)
            result, message = data.add_funds(add_fund)
            if not result:
                flash(message, category="danger")
                return redirect(url_for("home_page"))

            else:
                result, message = data.update_balance(fund_bal)
                if not result:
                    flash(message, category="danger")
                    return redirect(url_for("home_page"))

                else:
                    flash(message, category="success")
                    return redirect(url_for("home_page"))
        else:
            flash(f"something went wrong with validation", category="danger")
            return render_template("home.html", add_funds_forms=add_funds_forms)

    else:
        return render_template("home.html", add_funds_forms=add_funds_forms)
