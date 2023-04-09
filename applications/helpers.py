from __future__ import annotations
from flask import flash
from sqlalchemy import func
from nsepython import nse_holidays
from datetime import datetime, timedelta
import requests, zipfile, io, tempfile, os, shutil, csv
import yfinance as yf
import re



from applications.models import Transactions, db
from applications.database import app



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


class DownloadBhavcopy:

    def __init__(self) -> None:

        self.headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Brave/537.36'}
        self.response = requests.get('https://www.nseindia.com/api/marketStatus', headers=self.headers)
        # print(self.response.status_code)
        self.check_market_status()

    def check_market_status(self) -> None:

        try:
            self.response
            data = self.response.json()['marketState'][0]

            if data['marketStatus'] == "Closed":

                self.get_trading_date(data)

        except Exception as e:
            print(f"error: {self.response.status_code}")
       
    def get_trading_date(self, data):

        try:
            print("inside the try block")
            date_string = data['tradeDate']
            date = datetime.strptime(date_string, "%d-%b-%Y")
            self.get_bhav_copy(date)
        except Exception as e:
            print(f"Something went wrong: {e}")

    def get_bhav_copy(self, date):

        day = date.strftime("%d")
        month = date.strftime("%b").upper()
        year = date.year        
        filename = f"cm{day}{month}{year}bhav.csv"
        url = f"https://archives.nseindia.com/content/historical/EQUITIES/{year}/{month}/cm{day}{month}{year}bhav.csv.zip"
        response_2 = requests.get(url, headers=self.headers)

 
        try:
            with zipfile.ZipFile(io.BytesIO(response_2.content), 'r') as zip_ref:
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_ref.extractall(temp_dir)
                    os.rename(os.path.join(temp_dir, filename), os.path.join(temp_dir, 'bhav_copy.csv'))
                    shutil.move(os.path.join(temp_dir, 'bhav_copy.csv'), os.path.join(os.getcwd(), 'bhav_copy.csv'))
        except Exception as e:
            print(f"Something went wrong: {e}")
            pass
    
#----------------Stock Search---------------#
def lookup(symbol):

    not_found_in_bhavcopy = []

    if symbol == None:
        return False
    else:
        pattern = r"\b{}\b".format(re.escape(symbol))

        with open('bhav_copy.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)

            next(csv_reader)

            for line in csv_reader:
                if re.search(pattern, line[0]):
                    return True
            else:         
                not_found_in_bhavcopy.append(symbol)
            
            for nf_symb in not_found_in_bhavcopy:
                bo_symb = f"{nf_symb}.BO"
                if yf.Ticker(bo_symb):
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
     
# Function to return Previous Close from the downloaded bhav copy
def my_prev_close(symbol):

    not_found_in_bhavcopy = []
    if symbol == None:
        return False
    symb = chk_special(symbol)   

    try:
        pattern = r"\b{}\b".format(re.escape(symbol))

        with open('bhav_copy.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)

            for line in csv_reader:
                if re.search(pattern, line[0]) and line[1] == "EQ":
                    return float(line[7])
            else:
                not_found_in_bhavcopy.append(symbol)

            for nf_symb in not_found_in_bhavcopy:
                bo_symb = f"{nf_symb}.BO"
                obj = yf.Ticker(bo_symb)
                data = obj.history(period="id")
                return data['Close'][0]

    except Exception as e:
        flash(f"Something went wrong in my_prev_close(). error: {e}", category='danger')
        return False
    
app.jinja_env.globals.update(my_prev_close=my_prev_close)

def bhavcopy_date() -> str:
    try:
        
        with open('bhav_copy.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Get the first row

            for line in csv_reader:
                return line[10]
                break

    except Exception as e:
        flash(f"Something went wrong in my_prev_close(). error: {e}", category='danger')
        return False

app.jinja_env.globals.update(bhavcopy_date=bhavcopy_date)