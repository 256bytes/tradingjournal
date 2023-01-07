from flask import flash, redirect, render_template, url_for
from flask_login import login_user

#-------------User Packages --------------------#
from applications import app
from applications.forms import RegisterForm
from applications.models import Users
from applications.database import db

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()

    try:
        if form.validate_on_submit():
            user_to_create =     Users(username=form.username.data,
                                    email=form.email.data, 
                                    password=form.password.data
                                    )
            db.session.add(user_to_create)
            db.session.commit()
            login_user(user_to_create)
            flash(f'Account Created Successfully. You are logged in as {user_to_create.username}', category='success')
            flash(f'Add brokers details for {user_to_create.username}', category='info')
            return redirect(url_for('add_brokers_page'))
        if form.errors != {}:
            for err_msg in form.errors.values():
                flash(f'There was an error with Registration: {err_msg}', category='danger')
    except Exception as e:
        flash(f'something went wrong! error: {e}', category='danger')

    return render_template('register.html', form=form)