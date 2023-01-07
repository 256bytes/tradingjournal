from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user

#-------------User Packages --------------------#
from applications import app
from applications.forms import AddBrokersForm
from applications.models import Brokers, List_of_brokers
from applications.database import db


@app.route('/add_brokers', methods=['GET', 'POST'])
def add_brokers_page():

    form = AddBrokersForm()

    # This is to populate the list of brokers in ad brokers form.
    form.name.choices = [(list_of_brokers.id, list_of_brokers.name) for list_of_brokers in List_of_brokers.query.all()]

    if request.method == "POST":

        if form.validate_on_submit():
            broker_name = request.form.get('name')
            broker_code = request.form.get('trading_code')

            db.session.rollback()
            db.session.begin()
            # To check whether user has entered a unique code or duplicate code.
            check_duplicate = db.session.query(Brokers).filter(Brokers.trading_code == broker_code).first()

            if check_duplicate:
                flash(f"Already registered with same trader code", category='danger')
                return render_template('add_brokers.html', form=form)
            else:
                
                db.session.rollback()
                db.session.begin()
                # This will give us the details of the selected broker to enter the database of the user.
                broker_details = db.session.query(List_of_brokers).filter(List_of_brokers.id == broker_name).first()

                try:
                    add_broker_details = Brokers(user_id = current_user.id,
                                                name = broker_details.name,
                                                trading_code = broker_code,
                                                type = broker_details.type,
                                                equity_delivery = broker_details.equity_delivery,
                                                equity_intraday = broker_details.equity_intraday,
                                                transaction_chgs = broker_details.transaction_chgs,
                                                dp_chgs = broker_details.dp_chgs
                                                )
                    db.session.add(add_broker_details)
                    db.session.commit()
                    flash(f'Successfull! {broker_details.name} added.', category='success')
                    return redirect(url_for('settings_page'))
                except Exception as e:
                    flash(f"Something went wrong! error: {e}", category='danger')
                    return render_template('/add_brokers.html', form=form)
            
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with Registration: {err_msg}', category='danger')
            return render_template('add_brokers.html', form=form)
    else:
        return render_template('add_brokers.html', form=form)