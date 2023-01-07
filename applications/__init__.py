
import secrets
from flask import Flask



secret = secrets.token_urlsafe(32)

# My db connection
local_server = True
app = Flask(__name__)
app.secret_key = secret


# For comma seprated numbers
@app.template_filter()
def numberFormat(value):
    a = str(value).split('.')
    if len(a) > 1:
        if len(a[0]) >= 4:
            # return value
            return f'{a[0][:-3]},{a[0][-3:]}.{a[1]}'
        else:
            return value
    else:
        return f'{a[0][:-3]},{a[0][-3:]}.00'



from applications.routers import import_holdings_route, login_route, register_route, add_broker_route, settings_route, home_route, buy_route, notes_route,\
            holdings_route, profit_loss_route, analytic_route, logout_route
from applications.routers import analysis_import_route, sell_route, delete_analysis, add_bonus_route, sell_history_route, buy_history_route, delete_broker


# from applications import routes

