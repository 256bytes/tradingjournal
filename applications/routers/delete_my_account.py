from flask import redirect, url_for, request, flash
from flask_login import current_user, login_required

#-------------User Packages --------------------#
from applications import app
from applications.models import Transactions, Research, Funds, Brokers, Users
from applications.database import db

@app.route('/delete_my_account', methods=["GET", "POST"])
@login_required
def delete_my_account():
    
    if request.method == "POST":

        
        user_account_id = request.form.get('id')

        db.session.rollback()
        db.session.begin()
        try:
            Transactions.query.filter_by(user_id = user_account_id ).delete()
            Research.query.filter_by(user_id = user_account_id ).delete()
            Funds.query.filter_by(user_id = user_account_id ).delete()
            Brokers.query.filter_by(user_id = user_account_id ).delete()
            account_to_delete = Users.query.filter_by(id = user_account_id).first()
            db.session.delete(account_to_delete)
            db.session.commit()
            flash(f"Successfully deleted the account", category='success')
            return redirect(url_for('login_page'))

        except Exception as e:
            flash(f"Something went wrong error: {e}", category='warning')
            return redirect(url_for('holdings_page'))
    else:
        return redirect(url_for('holdings_page'))
