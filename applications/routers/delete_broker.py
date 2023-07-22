from flask import redirect, url_for, flash, request
from flask_login import current_user

#-------------User Packages --------------------#
from applications import app
from applications.user_database import GetUserData

@app.route("/delete_broker/<trading_code>", methods=["GET", "POST"])
def delete_broker(trading_code):
    t_code = trading_code
    data = GetUserData(user_id = current_user.id, trading_code = t_code)
    result, message = data.delete_my_broker_account()
    if not result:
        flash(message, category='danger')
        return redirect(url_for('settings_page'))
    else:
        flash(message, category='success')
        return redirect(url_for('home_page'))

    # if request.method == "POST":
    #     t_code = trading_code
    #     print()
    #     print(t_code)
    #     print()
    #     
    #     data = GetUserData(user_id = current_user.id)

    #     return t_code
    return trading_code
    #     #-------------User Packages --------------------#
    #     from applications.models import Brokers
    #     from applications.database import db
    #     try:
    #         db.session.rollback()
    #         db.session.begin()
    #         Brokers.query.filter(Brokers.user_id == current_user.id, Brokers.id == id).delete()
    #         db.session.commit()
    #     except Exception as e:
    #         flash(f"Something went wrong while deleting from the data to the database. error: {e}", category='warning')
    #         return redirect(url_for('settings_page'))
    # else:
    #     flash("Successfully deleted!", category='success')
    #     return redirect(url_for('settings_page'))