from flask import redirect, url_for, request, flash
from flask_login import current_user, login_required

#-------------User Packages --------------------#
from applications import app
from applications.models import Transactions
from applications.database import db

@app.route('/add_bonus', methods=["GET", "POST"])
@login_required
def add_bonus():

    if request.method == "POST":
        tc = request.form.get('tc')
        script = request.form.get('script')
        bonus = request.form.get('add_bonus')

        db.session.rollback()
        db.session.begin()
        try:
            # to get the broker name
            data = db.session.query(Transactions.broker).filter(Transactions.trading_code == tc).first()
        except Exception as e:
            flash(f"Something went wrong while reading the database. error: {e}", category='warning')
            return redirect(url_for('holdings_page'))
    
        try:
            script_to_add = Transactions(user_id = current_user.id,
                            type = "CNC",
                            call = 'Bonus',
                            script = script,
                            price = 0.00,
                            qty = bonus,
                            brokerage_per_unit = 0.00,
                            net_rate_per_unit = 0.00,
                            net_total_before_levies = 0.00,
                            transaction_chgs = 0.00,
                            dp_chgs = 0.00,
                            stt = 0.00,
                            sebi_turnover_fees = 0.00,
                            stamp_duty = 0.00,
                            gst = 0.00,
                            total_taxes = 0.00,
                            net_total = 0.00,
                            broker = data[0], # square braket to extract the data from the tupple
                            trading_code = tc
                            )
            db.session.add(script_to_add)
            db.session.commit()
            flash(f"{bonus} Bonus shares of {script} successfully added to {tc} account. ", category='success')
            return redirect(url_for('holdings_page'))
        except Exception as e:
            flash(f"Something went wrong while addding to the database. error: {e}", category='warning')
            return redirect(url_for('holdings_page'))

        
    return redirect(url_for('home_page'))