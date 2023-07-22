from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user

#-------------User Packages --------------------#
from applications import app


@app.route('/add_brokers', methods=['GET', 'POST'])
def add_brokers_page():

    #-------------User Packages --------------------#
    from applications.forms import AddBrokersForm
    from applications.models import List_of_brokers

    add_broker_form = AddBrokersForm()

    # This is to populate the list of brokers in ad brokers form.
    add_broker_form.name.choices = [(list_of_brokers.id, list_of_brokers.name) for list_of_brokers in List_of_brokers.query.all()]

    if request.method == "POST":

        if add_broker_form.validate_on_submit():

            from applications.validate_database import ValidateUserDatabase
            broker_id = add_broker_form.name.data # this returns choice numbers as entered in the database.
            trading_code = add_broker_form.trading_code.data

            user_broker_data = ValidateUserDatabase()
            result, message = user_broker_data.register_trader_code(trading_code)
            if result:
                flash(message, category='danger')
                return render_template('add_brokers.html', add_broker_form=add_broker_form)
                
            else:
                from applications.user_database import GetUserData
                add_user_broker = GetUserData()
                result, message = add_user_broker.add_broker_details(current_user.id, broker_id, trading_code)
                if result:
                    flash(message, category='success')
                    return redirect(url_for('settings_page'))

                else:
                    flash(message, category='danger')
                    return render_template('add_brokers.html', add_broker_form=add_broker_form)
            
    # if add_broker_form.errors != {}:
    #     for err_msg in add_broker_form.errors.values():
    #         flash(f'There was an error with Registration: {err_msg}', category='danger')
    #         return render_template('add_brokers.html', add_broker_form=add_broker_form)
    else:
        return render_template('add_brokers.html', add_broker_form=add_broker_form)