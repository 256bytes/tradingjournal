from flask import flash
from sqlalchemy import func
from nsepython import *
import requests
import yfinance as yf


from applications.models import Transactions
from applications.database import db


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

def lookup(symbol):
    if symbol == None:
        return False
    else:
        quote = nse_quote(symbol=symbol)
        if not quote:
            return False
        else:
            return True

# def ltp(symbol):
#     if symbol == None:
#         return False

#     try:
#         return(nse_quote_ltp(symbol=symbol))

#     except Exception as e:
#         print(e)
#         return False

def my_ltp(symbol):
    tick = symbol + ".NS"
    try:
        ltp = yf.download(tick)["Close"].iloc[-1]
        return ltp
    except Exception as e:
        flash("Couldn't find the last trading price.", category='info')
        return False
    # url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=NSE:{symbol}&apikey=4AA22TX42RKVS30F'
    # r = requests.get(url)
    # data = r.json()
    # print('\n')
    # print(f"this is from outside the for: {data}")
    # print('\n')
    # for i in data:
    #     print('\n')
    #     print(f"this is from for: {i}")
    #     print('\n')
# def nse_custom_function_secfno(symbol,attribute="lastPrice"):
#     positions = nsefetch('https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O')
#     endp = len(positions['data'])
#     for x in range(0, endp):
#         if(positions['data'][x]['symbol']==symbol.upper()):
#             return positions['data'][x][attribute]

# print(nse_custom_function_secfno("Reliance"))
# print(nse_custom_function_secfno("Reliance","pChange"))
