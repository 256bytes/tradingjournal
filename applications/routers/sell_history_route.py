from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

#-------------User Packages --------------------#
from applications import app
from applications.models import Transactions


@app.route('/sell_history')
@login_required
def sell_history_page():

    try:
        sell_page = request.args.get('page', 1, int)
        stocks_sold = Transactions.query.filter(Transactions.user_id == current_user.id,\
            Transactions.type == "CNC", Transactions.call == "Sell").order_by(Transactions.date.desc()).paginate(page=sell_page, per_page=10)
    except Exception as e:
        flash(f"Something went wrong while reading the database. error: {e}", category='warning')
        return redirect(url_for('home_page'))

    return render_template('sell_history.html',stocks_sold=stocks_sold)