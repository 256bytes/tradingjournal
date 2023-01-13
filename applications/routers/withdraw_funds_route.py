from flask import redirect, url_for, request, flash, render_template
from flask_login import current_user, login_required
from sqlalchemy import update

#-------------User Packages --------------------#
from applications import app
from applications.models import Funds
from applications.database import db
from applications.forms import WithdrawFunds


@app.route('/withdraw_funds', methods=["GET", "POST"])
@login_required
def withdraw_funds():
    
    withdraw_funds_form = WithdrawFunds()
    t_code = request.form.get('trader_code')
    amount = request.form.get('withdraw_funds')
    if not t_code:
        flash("Something went wrong while reading trading_code!", category='danger')
        return redirect(url_for('home_page'))
    
    if not amount or int(amount) < 0:
        flash("Something went wrong while reading amount", category='danger')
        return redirect(url_for('home_page'))
    try:
        db.session.rollback()
        db.session.begin()
        data = Funds(user_id = current_user.id,
                        trading_code = t_code,
                        pay_out = amount
                        )
        db.session.add(data)
        db.session.commit()
        flash(f"{amount} withdrawn from {t_code} account sucessfully!", category='success')
        return redirect(url_for('home_page'))
    except Exception as e:
        flash(f"Something went wrong while inserting the data to the database. error: {e}", category='warning')
        return redirect(url_for('home_page'))
    
    return render_template('home.html')

    return render_template('home.html', withdraw_funds_form=withdraw_funds_form)
