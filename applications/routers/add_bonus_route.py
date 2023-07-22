from flask import redirect, url_for, request, flash, render_template
from flask_login import current_user, login_required

# -------------User Packages --------------------#
from applications import app


@app.route("/add_bonus", methods=["GET", "POST"])
@login_required
def add_bonus():
    # -------------User Packages --------------------#
    from applications.forms import AddBonusForm
    from applications.user_database import GetUserData

    add_bonus = AddBonusForm()

    if request.method == "POST":
        
        if add_bonus.validate_on_submit():
            add_bonus_values = request.form.getlist('add_bonus')
            tc_values = request.form.getlist('trade_account')
            script = request.form.getlist('script')

            for add_bonus, trading_code, symbol in zip(add_bonus_values, tc_values, script):
                data = GetUserData(
                    user_id=current_user.id,
                    symbol=symbol,
                    price=0.00,
                    qty=add_bonus,
                    trading_code=trading_code,
                    call_type="Bonus",
                    trade_mode="CNC",
                )

            result, message = data.brokerage_and_taxes()
            if not result:
                flash(message, category="danger")
                return render_template("/home.html")
            else:
                result, message = data.add_transactions()
                if not result:
                    flash(message, category="danger")
                    return render_template("/home.html")
                else:
                    return redirect(url_for("holdings_page", page=1))

    return redirect(url_for("home_page"))
