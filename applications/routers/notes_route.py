from flask import render_template

#-------------User Packages --------------------#
from applications import app

@app.route('/notes')
def notes_page():
    return render_template('notes.html')