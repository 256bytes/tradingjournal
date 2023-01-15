from flask import request, flash, redirect, url_for
from flask_login import current_user, login_required
from openpyxl import load_workbook
import os

#-------------User Packages --------------------#
from applications import app
from applications.models import Brokers, Transactions
from applications.helpers import lookup, chk_special
from applications.database import db
from applications.calc_taxes.get_taxes import CaluculateBrokerageAndTaxes

@app.route('/data_import', methods=["GET","POST"])
@login_required
def import_data_form():
    call = "buy"

    if not request.files['File']:
        flash("Select the file to import", category='warning')
        return redirect(url_for('holdings_page'))

    try:
        f = request.files['File']
        f.save(f.filename)
        fname = (f.filename)
        book = load_workbook(fname)

        sheet = book.active

    except Exception as e:
        flash(f"Something went wrong while importing the file. error: {e}", category='warning')
        return redirect(url_for('holdings_page'))
    
    for row in range(2, sheet.max_row + 1):
        
        if sheet.cell(row, 1).value:
            try:
                tc = sheet.cell(row, 1).value
                type = sheet.cell(row, 2).value
                script = sheet.cell(row, 3).value
                price = sheet.cell(row, 4).value
                qty = sheet.cell(row, 5).value
                chk_script = lookup(script)
            except Exception as e:
                flash(f"Something went wrong while reading the file. error: {e}", category='warning')
                os.remove(f.filename)
                return redirect(url_for('holdings_page'))
                

            tc = tc.upper()
            chk_tc = db.session.query(Brokers.trading_code).filter(Brokers.user_id == current_user.id, Brokers.trading_code == tc).first()

            if chk_tc == None:
                flash(f"Invalid trading code: {tc}", category='danger')
                os.remove(f.filename)
                return redirect(url_for('holdings_page'))
            
            if not chk_tc.trading_code:
                flash(f"Trading code with {tc} not found", category='danger')
                os.remove(f.filename)
                return redirect(url_for('holdings_page'))
                break
            
            broker_name = db.session.query(Brokers.name).filter(Brokers.user_id == current_user.id, Brokers.trading_code == tc).first()

            if not chk_script:
                flash("Invalid symbol {script}", category='warning')
                os.remove(f.filename)
                return redirect(url_for('holdings_page'))
                break

            try:
                result = CaluculateBrokerageAndTaxes(tc, current_user.id, price, qty, call)
            except Exception as e:
                flash(f"Something went wrong while getting the result. error: {e}", category='warning')
                os.remove(f.filename)
                return redirect(url_for('holdings_page'))

            symb = chk_special(script)

            try:
                db.session.rollback()
                db.session.begin()
                script_to_add = Transactions(user_id = current_user.id,
                                type = "CNC",
                                call = 'Buy',
                                script = symb,
                                price = price,
                                qty = qty,
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
                                broker = broker_name.name,
                                trading_code = tc
                                )
                db.session.add(script_to_add)
                db.session.commit()
            except Exception as e:
                flash(f"Something went wrong while inserting the data to the database error: {e}", category='warning')
                os.remove(f.filename)
                return redirect(url_for('holdings_page'))
        else:
            os.remove(f.filename)
            break
    os.remove(f.filename)
    flash("Script successfully added!", category='success')
    return redirect(url_for('holdings_page'))