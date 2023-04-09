from flask import flash, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import func


#-------------User Packages --------------------#
from applications import app
from applications.forms import ResearchForms
from applications.models import Transactions, Research, Analysts
from applications.database import db
from applications.helpers import lookup


@app.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics_page():

    my_research_forms = ResearchForms()

    # Pagination logic
    page = request.args.get('page', 1, int)
    analysis = Research.query.filter(Research.user_id == current_user.id).order_by(Research.date.desc()).paginate(page=page, per_page=5)

    # to chk whether the said script is held by the user or not. if yes then reflect it in the page.
    chk_holdings = []
    for i in analysis:
        quantity = db.session.query(func.sum(Transactions.qty).label('holding')).filter(Transactions.user_id == current_user.id, Transactions.script == i.script).first()
        chk_holdings.append(quantity)

    if request.method == "POST":
        symbol = request.form.get('script').upper()
        script = lookup(symbol)
        if not script:
            flash('Invalid symbol', category="warning")
            return render_template('analytics.html', my_research_forms=my_research_forms, analysis=analysis)
        
        price = request.form.get('price')
        if int(price) < 0:
            flash('Price cannot be in negative', category="warning")
            return render_template('analytics.html', my_research_forms=my_research_forms, analysis=analysis)
        call = request.form.get('call').upper()
        sl = request.form.get('stop_loss')
        if int(sl) < 0:
            flash('Stop Loss cannot be in negative', category="warning")
            return render_template('analytics.html', my_research_forms=my_research_forms, analysis=analysis)
        target = request.form.get('target')
        if int(target) < 0:
            flash('Target cannot be in negative', category="warning")
            return render_template('analytics.html', my_research_forms=my_research_forms, analysis=analysis)
        tf = request.form.get('time_frame')
        if int(tf) < 0:
            flash('Time Frame cannot be in negative', category="warning")
            return render_template('analytics.html', my_research_forms=my_research_forms, analysis=analysis)

        # The input from the user is saved in analysts and research table
        #------------------ Logic to save the analyst related data to analyst table ----------------------#
        analyst = request.form.get('analyst')
        db.session.rollback()
        db.session.begin()
        get_analyst = Analysts.query.filter(Analysts.name == analyst).first()

        
        if not (get_analyst):
            db.session.rollback()
            db.session.begin()
            get_analyst = Analysts.query.filter(Analysts.name == analyst).first()

        
        if not (get_analyst):
            db.session.rollback()
            db.session.begin()
            add_analyst = Analysts(name = analyst,
                                number_of_calls = 1
                                )
            db.session.add(add_analyst)
            db.session.commit()
        else:
            db.session.rollback()
            db.session.begin()
            get_calls = db.session.query(Analysts.number_of_calls).filter(Analysts.name == analyst).first()
            get_analyst.number_of_calls = get_calls.number_of_calls +1

            db.session.add(get_analyst)
            db.session.commit()

            db.session.rollback()
            db.session.begin()
            add_analyst = Analysts(name = analyst,
                                number_of_calls = 1
                                )
            db.session.add(add_analyst)
            db.session.commit()
        #------------------ Logic to save the analyst related data to analyst table ends----------------------#

        #------------------ Logic to save the data to research table ----------------------#
        resource = request.form.get('resource')

        db.session.rollback()
        db.session.begin()
        add_research = Research (user_id = current_user.id,
                                script = symbol,
                                price = price,
                                call = call,
                                stop_loss = sl,
                                target = target,
                                time_frame = tf,
                                analyst = analyst,
                                resource = resource)
        db.session.add(add_research)
        db.session.commit()
        flash("Successfully added data to research table", category="success")
        return redirect(url_for('analytics_page'))
        
    return render_template('analytics.html', my_research_forms=my_research_forms, analysis=analysis, chk_holdings=chk_holdings)


# @app.route('/add_your_research', methods=['GET', 'POST'])
# def add_your_research_page():
#     my_research_forms = ResearchForms()
    
    # return render_template('add_your_research.html', my_research_forms=my_research_forms)