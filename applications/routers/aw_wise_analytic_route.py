from flask import request, flash, render_template
from flask_login import login_required, current_user

from applications import app
from applications.forms import AutoCompleteSearchForm, ResearchForms, StoplossTarget
from applications.user_database import chk_research_table


@app.route('/analyst_wise_analytics', methods=["GET", "POST"])
@login_required
def analyst_wise_analytics_page():
    
    caller = "analyst_wise_analytics_page"
    chk_research_table(current_user.id)

    from applications.user_database import GetUserData
    
    acs_form = AutoCompleteSearchForm()
    my_research_forms = ResearchForms()
    stoploss_target_forms = StoplossTarget()

    data = GetUserData(user_id=current_user.id)
    # analysts = acs_form.analyst.data
    analysts = request.args.get("analyst")
    y = request.args.get("caller")
    z = request.args.get("data")
    print()
    print("this is from analyst wise analytics page")
    print(y)
    print(z)
    print(analysts)
    print()
    # total_calls, total_open, total_live, total_target, total_closed = data.get_analyst_call_data(analysts)
    

    # result, message, ad, holdings = data.get_all_research_data()
    # research = message

    
    if request.method == "POST":

        if acs_form.analyst.data:
                analysts = acs_form.analyst.data
                total_calls, total_open, total_live, total_target, total_closed = data.get_analyst_call_data(analysts)
                print()
                print("this is from post")
                print(analysts)
                print()
                result, message, ad, holdings = data.get_analyst_wise_research_data(analysts)

                if not result:
                    flash(message, category='danger')
                    return render_template('/aw_analytic.html',
                                           analysts=analysts, 
                                           my_research_forms=my_research_forms,
                                           ad=ad,
                                           holdings=holdings,
                                           stoploss_target_forms=stoploss_target_forms,
                                           total_calls=total_calls,
                                            total_open=total_open,
                                            total_live=total_live,
                                            total_target=total_target,
                                            total_closed=total_closed,
                                            caller=caller
                                            )
                else:
                    return render_template('/aw_analytic.html',
                                           analysts=analysts,
                                           message=message,
                                           my_research_forms=my_research_forms,
                                           ad=ad,
                                           holdings=holdings,
                                           stoploss_target_forms=stoploss_target_forms,
                                           total_calls=total_calls,
                                            total_open=total_open,
                                            total_live=total_live,
                                            total_target=total_target,
                                            total_closed=total_closed,
                                            caller=caller

                                            )
        else:
            flash(f"something went wrong: {acs_form.analyst.data}", category='danger')
            return render_template('/analytics.html',
                                   research=research,
                                   my_research_forms=my_research_forms,
                                   total_calls=total_calls,
                                    total_open=total_open,
                                    total_live=total_live,
                                    total_target=total_target,
                                    total_closed=total_closed,
                                    caller=caller

                                    )
    
    elif request.method == "GET":
        x = acs_form.analyst.data
        
        analysts = request.args.get("analyst")
        total_calls, total_open, total_live, total_target, total_closed = data.get_analyst_call_data(analysts)
        result, rsrch_message, ad, holdings = data.get_all_research_data()
        research = rsrch_message
       
        print()
        print("get method")
        print(x)
        print(analysts)
        print()

        result, message, ad, holdings = data.get_analyst_wise_research_data(analysts)
        if not result:
            flash(message, category='danger')
            return render_template('/analytics.html',
                                   research=research,
                                   my_research_forms=my_research_forms,
                                   total_calls=total_calls,
                                    total_open=total_open,
                                    total_live=total_live,
                                    total_target=total_target,
                                    total_closed=total_closed,
                                            caller=caller

                                    )

        else:
            return render_template('/aw_analytic.html',
                                   analysts=analysts,
                                   message=message,
                                   my_research_forms=my_research_forms,
                                   ad=ad,
                                   holdings=holdings,
                                   stoploss_target_forms=stoploss_target_forms,
                                   total_calls=total_calls,
                                    total_open=total_open,
                                    total_live=total_live,
                                    total_target=total_target,
                                    total_closed=total_closed,
                                            caller=caller

                                    )
             
    else:              
        return render_template('/analytics.html',
                               analysts=analysts,
                               research=research,
                               my_research_forms=my_research_forms,
                               total_calls=total_calls,
                                total_open=total_open,
                                total_live=total_live,
                                total_target=total_target,
                                total_closed=total_closed,
                                            caller=caller

                                )
    
    