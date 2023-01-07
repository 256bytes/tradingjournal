from flask import redirect, url_for, flash
from flask_login import current_user

#-------------User Packages --------------------#
from applications import app
from applications.models import Research
from applications.database import db



@app.route('/delete_analysis/<id>', methods=["GET","POST"])
def delete_analysis(id):

    try:
        db.session.rollback()
        db.session.begin()
        Research.query.filter(Research.user_id == current_user.id, Research.id == id).delete()
        db.session.commit()
    except Exception as e:
        flash(f"Something went wrong while deleting from the data to the database. error: {e}", category='warning')
        return redirect(url_for('analytics_page'))

    flash("Successfully deleted!", category='success')
    return redirect(url_for('analytics_page'))