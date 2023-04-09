from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from sqlalchemy import update

#-------------User Packages --------------------#
from applications import app
from applications.forms import UpdateForm, AddFunds, DeleteMyAccount
from applications.models import Brokers, Users, Taxes
from applications.database import db


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings_page():

    delete_my_account = DeleteMyAccount()
    users = Users.query.filter_by(id=current_user.id)
    taxes = Taxes.query.all()
    broker_query = Brokers.query.filter_by(user_id=current_user.id)
    broker_data = Brokers.query.filter(Brokers.user_id == current_user.id).all()
    add_funds_form = AddFunds()
    update_form = UpdateForm()
    brokers_id = request.form.get('brokers_id')

    if request.method == "POST":
        #-Check and Update
        new_eq_dv_val = request.form.get('new_equity_delivery')
        old_eq_dv_val = request.form.get('old_equity_delivery')
        if old_eq_dv_val != new_eq_dv_val: #-------------------------------------------Check if there is any change.
            
            try:
                db.session.rollback()
                db.session.begin()
                # update
                u = update(Brokers)
                u = u.values({"equity_delivery": new_eq_dv_val})
                u = u.where(Brokers.id == brokers_id)
                db.engine.execute(u)
                db.session.commit()
                flash("Successfully updated! Equity Delivery Charges", category='success')
                
            except Exception as e:
                flash(f"Something went wrong: {e}", category='danger')
        #------------------------------------------------------------------------Check and Update
        new_eq_it_val = request.form.get('new_equity_intraday')
        old_eq_it_val = request.form.get('old_equity_intraday')
        if old_eq_it_val != new_eq_it_val: #-------------------------------------Check if there is any change.
            try:
                db.session.rollback()
                db.session.begin()
                #update
                u = update(Brokers)
                u = u.values({"equity_intraday": new_eq_it_val})
                u = u.where(Brokers.id == brokers_id)
                db.engine.execute(u)
                db.session.commit()
                flash("Successfully updated! Equity Intraday Charges", category='success')
            except Exception as e:
                flash(f"Something went wrong: {e}",category="danger")

        #------------------------------------------------------------------------Check and Update
        new_dp_val = request.form.get('new_dp_chgs')
        old_dp_val = request.form.get('old_dp_chgs')
        if old_dp_val != new_dp_val: #-------------------------------------------Check if there is any change.
            try:
                db.session.rollback()
                db.session.begin()
                #update
                u = update(Brokers)
                u = u.values({"dp_chgs": new_dp_val})
                u = u.where(Brokers.id == brokers_id)
                db.engine.execute(u)
                db.session.commit()
                flash("Successfully updated! Dp Charges", category='success')
                return redirect(url_for('settings_page'))
            except Exception as e:
                flash(f"Something went wrong: {e}",category="danger")
                return render_template('home.html')

        
    return render_template('/settings.html', broker_query=broker_query, update_form=update_form, users=users, taxes=taxes, broker_data=broker_data, add_funds_form=add_funds_form, delete_my_account=delete_my_account)