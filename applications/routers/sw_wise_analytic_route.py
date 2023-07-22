from flask import request, flash, render_template
from flask_login import login_required, current_user


from applications import app
from applications.forms import AutoCompleteSearchForm, ResearchForms, StoplossTarget
from applications.user_database import chk_research_table


@app.route('/script_wise_analytics<int:page>', methods=["GET", "POST"])
@login_required
def script_wise_analytics_page(page):

    chk_research_table(current_user.id)

    from applications.user_database import GetUserData

    acs_form = AutoCompleteSearchForm()
    my_research_forms = ResearchForms()
    stoploss_target_forms = StoplossTarget()

    if request.method == "POST":
        if acs_form.research_symbols.data:
            symbol = acs_form.research_symbols.data

            data = GetUserData(user_id = current_user.id, symbol=symbol)

            result, message, ad, holdings = data.get_script_wise_research_data()

            if not result:
                flash(message, category='danger')
                return render_template('/sw_analytic.html',  my_research_forms=my_research_forms, ad=ad, holdings=holdings, stoploss_target_forms=stoploss_target_forms)

            else:
                return render_template('/sw_analytic.html', message=message, my_research_forms=my_research_forms, holdings=holdings, stoploss_target_forms=stoploss_target_forms, ad=ad)
        
        else:
            flash(f"something went wrong: {acs_form.analyst.data}", category='danger')
            return render_template('/analytics.html', my_research_forms=my_research_forms)
    

    return render_template('/analytics.html', my_research_forms=my_research_forms)