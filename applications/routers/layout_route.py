

from applications import app
from applications.forms import AutoCompleteSearchForm

@app.context_processor
def layout_page():
    acs_form = AutoCompleteSearchForm()
    return dict(acs_form=acs_form)
