from flask import redirect, url_for, request, flash, render_template
from flask_login import current_user, login_required
from sqlalchemy import update

#-------------User Packages --------------------#
from applications import app
from applications.models import Funds
from applications.database import db


@app.route('/add_funds', methods=["GET", "POST"])
@login_required
def add_funds():

    t_code = request.form.get('trader_code')
    amount = request.form.get('add_funds')
    try:
        db.session.rollback()
        db.session.begin()
        data = Funds(user_id = current_user.id,
                        trading_code = t_code,
                        pay_in = amount
                        )
        db.session.add(data)
        db.session.commit()
        flash("Script successfully added!", category='success')
        return redirect(url_for('home_page'))
    except Exception as e:
        flash(f"Something went wrong while inserting the data to the database. error: {e}", category='warning')
        return redirect(url_for('home_page'))
    
    return render_template('home.html')


