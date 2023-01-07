from flask import flash, redirect, url_for, session
from flask_login import logout_user
from sqlalchemy import func


#-------------User Packages --------------------#
from applications import app


@app.route('/logout')
def logout_page():
    logout_user()
    session.clear()
    flash('You are logged out!', category='info')
    return redirect(url_for('login_page'))