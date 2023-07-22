from flask import flash, render_template
from flask_login import login_required, current_user

from applications import app
from applications.forms import AutoCompleteSearchForm, ResearchForms, StoplossTarget
from applications.user_database import chk_research_table



@app.route('/live_calls', methods=["GET", "POST"])
@login_required
def live_calls_page():
    caller = "live_calls_page"
    chk_research_table(current_user.id)

    acs_form = AutoCompleteSearchForm()
    my_research_forms = ResearchForms()
    stoploss_target_forms = StoplossTarget()

    from applications.user_database import GetUserData
    data = GetUserData(user_id = current_user.id)
    total_calls, total_open, total_live, total_closed = data.get_call_data()

    result, message, ad, holdings = data.get_all_open_calls()
    if not result:
        flash(message, category='danger')
        return render_template('/live_call_analytic.html',
                               my_research_forms=my_research_forms,
                               ad=ad,
                               holdings=holdings,
                               stoploss_target_forms=stoploss_target_forms,
                               total_calls=total_calls,
                                total_open=total_open,
                                total_live=total_live,
                                total_closed=total_closed,
                                caller=caller
                                )
    else:
        return render_template('/live_call_analytic.html',
                               message=message,
                               my_research_forms=my_research_forms,
                               ad=ad,
                               holdings=holdings,
                               stoploss_target_forms=stoploss_target_forms,
                               total_calls=total_calls,
                                total_open=total_open,
                                total_live=total_live,
                                total_closed=total_closed,
                                caller=caller
                                )

    