from flask import redirect, url_for, flash, request
from flask_login import current_user

#-------------User Packages --------------------#
from applications import app

@app.route('/delete_analysis/<id>', methods=["GET", "POST"])
def delete_analysis(id):

    if request.method == "POST":
    
        print()
        print("inside the delete research")
        print()
        return redirect(url_for('analytics_page'))

    #-------------User Packages --------------------#
        from applications.models import Research
        from applications.database import db
        try:
            Research.query.filter(Research.user_id == current_user.id, Research.id == id).delete()
            db.session.commit()
            flash("Successfully deleted!", category='success')
            return redirect(url_for('analytics_page'))

        except Exception as e:
            flash(f"Something went wrong while deleting from the data to the database. error: {e}", category='warning')
            return redirect(url_for('analytics_page'))
    else:
        return redirect(url_for('analytics_page'))