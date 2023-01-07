from flask import flash, redirect, render_template, url_for
from flask_login import login_user


#-------------User Packages --------------------#
from applications import app
from applications.forms import LoginFrom
from applications.models import Users

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    
    form = LoginFrom()
    if form.validate_on_submit():

        attempted_user = Users.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
            ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash(f'Username and password mismatch! Please try again', category='danger')
    return render_template('login.html', form=form)