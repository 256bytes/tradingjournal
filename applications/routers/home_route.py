from flask import render_template

#-------------User Packages --------------------#
from applications import app


@app.route('/home', methods=['GET', 'POST'])
def home_page():#------------------------------------------------------------------------------------------------------------------Home Page
    return render_template('/home.html')