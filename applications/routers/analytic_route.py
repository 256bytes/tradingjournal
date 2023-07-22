from flask import flash, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import func
from applications import app
import bleach

@app.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics_page():

    #-------------User Packages --------------------#
    from applications.forms import ResearchForms, StoplossTarget, AutoCompleteSearchForm
    from applications.models import Transactions
    from applications.database import db
    from applications.user_database import GetUserData
    
    from applications.user_database import chk_research_table

    chk_research_table(current_user.id)

    my_research_forms = ResearchForms()
    stoploss_target_forms = StoplossTarget()
    acs_form = AutoCompleteSearchForm()

    data = GetUserData(user_id = current_user.id)
    total_calls, total_open, total_live, total_closed = data.get_call_data()
    result, message, ad, holdings = data.get_all_research_data()
    if not result:
        flash(message, category='danger')
        return render_template('home.html')
    else:
        research = message

    if request.method == "POST":
        from applications.helpers import SymbolLookup

        # --------------------------------- Validating the inputs -----------------------------------------------
        if my_research_forms.validate_on_submit():
            symbol = my_research_forms.script.data.upper()
            price = my_research_forms.price.data
            call_type = my_research_forms.call.data.capitalize()
            stop_loss = my_research_forms.stop_loss.data
            target = my_research_forms.target.data
            call_validity = my_research_forms.call_validity.data
            analyst = my_research_forms.analyst.data.capitalize()
            resource = my_research_forms.resource.data
            tgt_sl = my_research_forms.tgt_sl.data

            # ----- Validates stock symbol ----------------------------
            validate_stock_symbol = SymbolLookup().find_symbol(symbol)

            if validate_stock_symbol:
                
                data = GetUserData(route='/analytics',user_id=current_user.id, symbol=symbol, call_type=call_type, price=price)
                
                result, message = data.update_research(stop_loss, target, call_validity, analyst, resource,)
                if not result:
                    flash(message, category='danger')
                    return render_template('analytics.html',
                                           acs_form=acs_form,
                                            tgt_sl=tgt_sl,
                                            my_research_forms=my_research_forms,
                                            research=research,
                                            holdings=holdings,
                                            stoploss_target_forms=stoploss_target_forms,
                                            total_calls=total_calls,
                                                total_open=total_open,
                                                total_live=total_live,
                                                total_closed=total_closed
                                        )
                
                else:
                    result, message = data.update_analyst(analyst=analyst)
                    if not result:
                        flash(message, category='danger')
                        return render_template('analytics.html',
                                               acs_form=acs_form,
                                                tgt_sl=tgt_sl,
                                                my_research_forms=my_research_forms,
                                                research=research,
                                                holdings=holdings,
                                                stoploss_target_forms=stoploss_target_forms,
                                                total_calls=total_calls,
                                                    total_open=total_open,
                                                    total_live=total_live,
                                                    total_closed=total_closed
                                            )
                    else:
                        flash(message, category='success')
                        return render_template('analytics.html',
                                               acs_form=acs_form,
                                                tgt_sl=tgt_sl,
                                                my_research_forms=my_research_forms,
                                                research=research,
                                                holdings=holdings,
                                                stoploss_target_forms=stoploss_target_forms,
                                                total_calls=total_calls,
                                                    total_open=total_open,
                                                    total_live=total_live,
                                                    total_closed=total_closed
                                                )
        
            else:
                return render_template('analytics.html',
                                    acs_form=acs_form,
                                    tgt_sl=tgt_sl,
                                    my_research_forms=my_research_forms,
                                    research=research,
                                    holdings=holdings,
                                    stoploss_target_forms=stoploss_target_forms,
                                    total_calls=total_calls,
                                        total_open=total_open,
                                        total_live=total_live,
                                        total_closed=total_closed
                                )
        else:
            return render_template('analytics.html',
                                   acs_form=acs_form,
                                #    tgt_sl=tgt_sl,
                                   my_research_forms=my_research_forms,
                                   research=research,
                                   holdings=holdings,
                                   stoploss_target_forms=stoploss_target_forms,
                                   total_calls=total_calls,
                                    total_open=total_open,
                                    total_live=total_live,
                                    total_closed=total_closed
                               )
    else:
        return render_template('analytics.html',
                               acs_form=acs_form, 
                               ad=ad, 
                               my_research_forms=my_research_forms, 
                               research=research, 
                               holdings=holdings, 
                               stoploss_target_forms=stoploss_target_forms,
                               total_calls=total_calls,
                               total_open=total_open,
                               total_live=total_live,
                               total_closed=total_closed
                               )
