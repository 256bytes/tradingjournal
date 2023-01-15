from flask import flash
from sqlalchemy import func
from nsepython import *

from applications.models import Transactions
from applications.database import db, app



def multiple_group(user_id, groupby):
	stock_data = db.session.query(
		*groupby,
		Transactions.script,
		Transactions.trading_code,
		func.sum(Transactions.qty).label('total_qty')
	)\
	.filter(
		Transactions.user_id == user_id,
		Transactions.type == "CNC")\
	.group_by(*groupby).all()
	
	return stock_data




#----------------Stock Search---------------#
def lookup(symbol):
    if symbol == None:
        return False
    else:
        quote = nse_quote(symbol=symbol)
        if not quote:
            return False
        else:
            return True


# Function checks if the string
# contains any ampersand character
def chk_special(string):

    for esc in string:
        # if found it would replace it
        if esc == '&':
            result = string.replace('&', '_')
            return result
        elif esc == "_":
            result = string.replace('_', '&')
            return result
        
    return string
     

def my_ltp(symbol):
    
    if symbol == None:
        return False
    symb = chk_special(symbol)     
    try:
        return nse_eq(symb)['priceInfo']['lastPrice']

    except Exception as e:
        flash(f"Something went wrong in my_ltp(). error: {e}", category='danger')
        return False
app.jinja_env.globals.update(my_ltp=my_ltp)


#--------- Yahoo finance -----------------------#

# def my_ltp(symbol):
#     symb = chk_special(symbol)
#     tick = symb + ".NS"
#     try:
#         ltp = yf.download(tick)["Close"].iloc[-1]
#         return ltp
#     except Exception as e:
#         flash("Couldn't find the last trading price.", category='info')
#         return False
