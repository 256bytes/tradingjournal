from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from applications import app


@app.route('/pl_broker_wise', methods=["GET"])
@login_required
def pl_broker_wise_page():

    from applications.user_database import GetUserData
    data = GetUserData(user_id = current_user.id)
    
    result, message = data.get_broker_wise_pl_data()
    if not result:
        flash(message, category='danger')
        return redirect(url_for('home_page'))
    else:

        return render_template('/pl_broker_wise.html', message=message)