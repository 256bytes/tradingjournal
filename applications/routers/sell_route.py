from flask import flash, redirect, url_for, request, render_template
from flask_login import current_user, login_required
from sqlalchemy import func

#-------------User Packages --------------------#
from applications import app
from applications.models import Brokers, Transactions
from applications.database import db
from applications.calc_taxes.get_taxes import CaluculateBrokerageAndTaxes

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell_page():
    call = "sell"

    if request.method == 'POST':
        script = request.form.get('script')
        t_code = request.form.get('code')

        #-This is to get number of shares held in result particular account
        try:
            db.session.rollback()
            db.session.begin()
            get_qty = db.session.query(func.sum(Transactions.qty).label('net_qty'))\
                    .filter(Transactions.user_id == current_user.id, Transactions.trading_code == t_code,\
                        Transactions.script == script, Transactions.type == "CNC").group_by(Transactions.trading_code).first()
        except Exception as e:
            flash(f"Something went wrong while fetching the net qty from the database. error: {e}", category='warning')
            return redirect(url_for('holdings_page'))


        sell_qty = (request.form.get('shares_to_sell'))
        sell_price = (request.form.get('new_sell_price'))

        # to get the brokers name
        db.session.rollback()
        db.session.begin()
        data = db.session.query(Brokers.name).filter(Brokers.trading_code == t_code).first()

        if sell_qty != None:
            if int(sell_qty) <= 0:
                flash('Quantity must greater than zero!', category='danger')
                return redirect(url_for('sell_page'))
            elif (get_qty.net_qty) <= 0:
                flash(f'You do not have any {script} shares with {t_code} Try with other account\s', category='danger')
                return redirect(url_for('sell_page'))
            elif int(sell_qty) > int(get_qty.net_qty):
                flash(f'Maximum shares you can sell is: {get_qty.net_qty} from {t_code}', category='danger')
                return redirect(url_for('sell_page'))
            
            try:
                # compute taxes and other charges.
                result = CaluculateBrokerageAndTaxes(t_code, current_user.id, float(sell_price), int(sell_qty), call)
            except Exception as e:
                flash(f"Something went wrong while getting the result. error: {e}", category='warning')
                return redirect(url_for('sell_page'))

            try:
                db.session.rollback()
                db.session.begin()  
                script_to_add = Transactions(user_id = current_user.id,
                                type = "CNC",
                                call = "Sell",
                                script = script,
                                price = sell_price,
                                qty = -int(sell_qty),
                                brokerage_per_unit = result.r_b,
                                net_rate_per_unit = result.r_rpu,
                                net_total_before_levies = result.r_net_before_tax,
                                transaction_chgs = result.r_tchgs,
                                dp_chgs = result.r_dp_chgs,
                                stt = result.r_stt,
                                sebi_turnover_fees = result.r_sebi,
                                stamp_duty = result.r_sd,
                                gst = result.r_gst,
                                total_taxes = result.r_total_taxes_others,
                                net_total = -int(result.r_payable),
                                broker = data.name,
                                trading_code = t_code
                                )
                db.session.add(script_to_add)
                db.session.commit()
                flash(f"Transactions was successful! Sold {sell_qty} shares of {script} at {sell_price}/-", category='success')
                return redirect(url_for('holdings_page'))

            except Exception as e:
                flash(f"Something went wrong while inserting the data to the database. error: {e}", category='warning')
                return redirect(url_for('sell_page'))
  
    return render_template('sell.html')

