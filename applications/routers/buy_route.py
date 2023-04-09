from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

#-------------User Packages --------------------#
from applications import app
from applications.forms import BuyForm
from applications.models import Brokers, Users, Transactions, Funds
from applications.database import db
from applications.helpers import lookup, chk_special
from applications.calc_taxes.get_taxes import CalculateBrokerageAndTaxes



@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy_page():

    call = "buy"
    buy_form = BuyForm()
    
    # to populate the users trading codes in buy form.
    db.session.rollback()
    db.session.begin()
    t_code = db.session.query(Brokers.trading_code).filter(Brokers.user_id == current_user.id) 
    
    if request.method == "POST":
        #--------------------------- Checking input of symbol/stock field ---------------------------------
        symbol = request.form.get('symbol').upper()
        script = lookup(symbol)
        if not symbol:
            flash("Field cannot be blank", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)
        elif not script:
            flash("Enter a Valid Symbol", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)

        symb = chk_special(symbol)
        
        #--------------------------- Checking input of price field ---------------------------------------
        try:
            price = float(request.form.get('price'))
        except Exception as e:
            flash(f'Invalid input: {e}', category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)
        if price <= 0:
            flash("Enter positive value", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)
        if not price:
            flash("Value must be greater than Zero", category='danger')
        
        #-------------------------- Checking input of quantity field ---------------------------------------
        try:
            share_qty = int(request.form.get('quantity'))
        except:
            flash("Quantity must be an Integer", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)
        if share_qty <= 0:
            flash("Quantity must be more than 0", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)

        #------------------------- Checking input of broker's code field -------------------------------------
        code = request.form.get('code').upper()
        attempted_code = Brokers.query.filter_by(trading_code=code, user_id=current_user.id).first()
        if not code:
            flash("Field cannot be empty.", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)
        elif not attempted_code:
            flash ("Enter a valid trading_code", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)

        #-------------------------- to get the broker's name ---------------------------------------------------
        data = db.session.query(Brokers.name).filter(Brokers.trading_code == code).first() 
        attempted_user = Users.query.filter_by(id=current_user.id).first()

        if not attempted_user:
            flash ("Invalid User or something went wrong!", category='danger')
            return render_template('/home.html', buy_form=buy_form, t_code=t_code)

        try:
            result = CalculateBrokerageAndTaxes(code, current_user.id, price, share_qty, call)
        except Exception as e:
                flash(f"Something went wrong while calculating brokerage and taxes. error: {e}", category='warning')
                return redirect(url_for('holdings_page'))

        #-------------------------- Updating Funds table ---------------------------------------------------
        try:
            db.session.rollback()
            db.session.begin()
            update_funds = Funds(user_id = current_user.id,
                                trading_code = code,
                                debits = result.r_payable)
            db.session.add(update_funds)
            db.session.commit()
        except Exception as e:
            flash(f"Something went wrong while inserting the data to the funds table. error: {e}", category='warning')
            return redirect(url_for('buy_page'))

        try:
            db.session.rollback()
            db.session.begin()
            script_to_add = Transactions(user_id = current_user.id,
                            type = "CNC",
                            call = 'Buy',
                            script = symb,
                            price = buy_form.price.data,
                            qty = buy_form.quantity.data,
                            brokerage_per_unit = result.r_b,
                            net_rate_per_unit = result.r_rpu,
                            net_total_before_levies = result.r_net_before_tax,
                            transaction_chgs = result.r_tchgs,
                            dp_chgs = result.r_dp_chgs,
                            stt = result.r_stt,
                            sebi_turnover_fees = result.r_turn_over,
                            stamp_duty = result.r_sd,
                            gst = result.r_gst,
                            total_taxes = result.r_total_taxes_others,
                            net_total = result.r_payable,
                            broker = data[0], # square braket to extract the data from the tupple
                            trading_code = code
                            )
            db.session.add(script_to_add)
            db.session.commit()
            flash("Script successfully added!", category='success')
            return redirect(url_for('holdings_page'))
        except Exception as e:
            flash(f"Something went wrong while inserting the data to the transaction table. error: {e}", category='warning')
            return redirect(url_for('buy_page'))
    else:
        return render_template('/buy.html', buy_form=buy_form, t_code=t_code)