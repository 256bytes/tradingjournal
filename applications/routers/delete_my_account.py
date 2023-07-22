from flask import redirect, url_for, request, flash
from flask_login import current_user, login_required

#-------------User Packages --------------------#
from applications import app

@app.route('/delete_my_account', methods=["GET", "POST"])
@login_required
def delete_my_account():
    

    if request.method == "POST":

        #-------------User Packages --------------------#
        from applications.user_database import GetUserData
        
        user_account_id = request.form.get('id')
        user_account_id = int(user_account_id)
        
        if user_account_id == current_user.id:

            user_data = GetUserData(user_id=user_account_id)
            result, message = user_data.delete_my_account()
            if not result:
                flash(message, category='danger')
                return redirect(url_for('register_page'))
            else:
                flash(message, category='success')
                return redirect(url_for('settings_page'))
        else:
            flash(f"User account id mismatch.", category='warning')
            return redirect(url_for('settings_page'))

    else:
        return redirect(url_for('settings_page'))
