
from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_required



from applications import app

@app.route("/stop_loss_target", methods=["GET", "POST"])
def stop_loss_target_page():

    if request.method == "POST":

        option = request.form.get('sl_target')
        row_id = request.form.get('id')
        date = request.form.get('date')
        symbol = request.form.get('script')
        call_validity = request.form.get('call_validity')
        analyst_name = request.form.get('analyst')
        tgt_sl = option


        from applications.user_database import GetUserData
        data = GetUserData(user_id=current_user.id, symbol=symbol)
        # result, message = data.get_tgt_sl_status(row_id, call_validity, analyst_name)
        # if not result:
        #     flash (message, category='danger')
        #     return render_template('home.html')
            
  
        result, message = data.update_tgt_sl_column_research(row_id, call_validity, analyst_name, tgt_sl)
        print(f"from update_tgt_sl column research .py else block {tgt_sl}")
        print()
        if not result:
            flash (message, category='danger')
            return render_template('home.html')
            
        else:
            result, message = data.update_sl_tgt_analyst_tabl(analyst_name, option, symbol, row_id, date)
            if not result:
                flash (message, category='danger')
                return render_template('home.html')
            else:
                # flash (message, category='success')
                return redirect(url_for('analytics_page'))
    else:
        return render_template('home.html')
 
