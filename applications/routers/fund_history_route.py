from flask import render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func


from applications import app
from applications.models import Funds



@app.route('/fund_history_page', methods=['GET', 'POST'])
@login_required
def fund_history_page():
    page = request.args.get('page', 1, int)
    fund_data = Funds.query.filter(Funds.user_id == current_user.id).paginate(page=page, per_page=10)

    return render_template('fund_history.html', fund_data=fund_data)