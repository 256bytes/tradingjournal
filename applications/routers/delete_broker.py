from flask import redirect, url_for, flash
from flask_login import current_user

#-------------User Packages --------------------#
from applications import app
from applications.models import Brokers
from applications.database import db

@app.route("/delete_broker/<id>", methods=["GET", "POST"])
def delete_broker(id):

    try:
        db.session.rollback()
        db.session.begin()
        Brokers.query.filter(Brokers.user_id == current_user.id, Brokers.id == id).delete()
        db.session.commit()
    except Exception as e:
        flash(f"Something went wrong while deleting from the data to the database. error: {e}", category='warning')
        return redirect(url_for('settings_page'))

    flash("Successfully deleted!", category='success')
    return redirect(url_for('settings_page'))