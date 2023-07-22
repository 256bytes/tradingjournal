import secrets
from flask import Flask, flash


secret = secrets.token_urlsafe(32)

# My db connection
local_server = True
app = Flask(__name__)

app.secret_key = secret


# For comma separated numbers
@app.template_filter()
def numberFormat(value):
    a = str(value).split(".")
    if len(a) > 1:
        if len(a[0]) >= 4:
            # return value
            return f"{a[0][:-3]},{a[0][-3:]}.{a[1]}"
        else:
            return value
    else:
        return f"{a[0][:-3]},{a[0][-3:]}.00"


from applications.routers import (
    acs_route,
    add_funds_route,
    import_holdings_route,
    live_calls_route,
    login_route,
    pl_script_wise_route,
    register_route,
    add_broker_route,
    settings_route,
    home_route,
    buy_route,
    notes_route,
    holdings_route,
    profit_loss_route,
    analytic_route,
    logout_route,
    stop_loss_target,
    broker_wise_holdings,
    pl_broker_wise_route,
    sw_wise_analytic_route,
    aw_wise_analytic_route,
)
from applications.routers import (
    analysis_import_route,
    sell_route,
    delete_analysis,
    add_bonus_route,
    sell_history_route,
    buy_history_route,
    delete_broker,
    fund_history_route,
    withdraw_funds_route,
    bonus_history_route,
    delete_my_account,
    get_transactions_details_route,
    script_wise_holdings,
    layout_route,
)

# from applications.helpers import my_prev_close
from applications.helpers import DownloadBhavcopy

DownloadBhavcopy()
