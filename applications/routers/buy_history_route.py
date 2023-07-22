from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required



#-------------User Packages --------------------#
from applications import app

@app.route('/buy_history')
@login_required
def buy_history_page():

    trade_mode = "CNC"
    #-------------User Packages --------------------#
    from applications.models import Transactions
    try:
        buy_page = request.args.get('page', 1, int)
        stocks_bought = Transactions.query.filter(Transactions.user_id == current_user.id,\
            Transactions.trade_mode == trade_mode, Transactions.call != "Sell").order_by(Transactions.date.desc()).paginate(page=buy_page, per_page=10)
    except Exception as e:
        flash(f"Something went wrong while reading the database. error: {e}", category='warning')
        return redirect(url_for('home_page'))

    return render_template('buy_history.html',stocks_bought=stocks_bought)