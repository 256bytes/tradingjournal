from __future__ import annotations
from flask import flash
from sqlalchemy import func


import time
from datetime import datetime
import requests, zipfile, io, tempfile, os, shutil, csv
import yfinance as yf
import re
import os
import glob

from applications.models import Transactions, db
from applications.database import app


def multiple_group(user_id, groupby):
    stock_data = (
        db.session.query(
            *groupby, Transactions.script, Transactions.trading_code, func.sum(Transactions.qty).label("total_qty")
        )
        .filter(Transactions.user_id == user_id, Transactions.trade_mode == "CNC")
        .group_by(*groupby)
        .all()
    )

    return stock_data


class DownloadBhavcopy:
    def __init__(self) -> None:
        self.set_headers()
        self.set_response()
        self.set_data()
        self.set_date_string()
        self.set_trade_date()
        self.set_filename()
        self.set_path()
        self.set_file()
        self.set_old_file_name_to_remove()
        self.check_is_bhavcopy()

    def set_headers(self):
        try:
            self.headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Brave/537.36"
            }
        except Exception as e:
            return (False, f"Something went wrong with setting headers. {e}")

    def set_response(self):
        try:
            self.response = requests.get("https://www.nseindia.com/api/marketStatus", headers=self.headers)
            time.sleep(5)
        except Exception as e:
            return (False, f"Something went wrong with setting response. {e}")

    def set_data(self):
        try:
            self.data = self.response.json()["marketState"][0]
        except Exception as e:
            return (False, f"Something went wrong with setting data. {e}")

    def set_date_string(self):
        try:
            self.date_string = self.data["tradeDate"]
        except Exception as e:
            return (False, f"Something went wrong with setting date_string. {e}")

    def set_trade_date(self):
        try:
            self.trade_date = datetime.strptime(self.date_string, "%d-%b-%Y").date()
        except Exception as e:
            return (False, f"Something went wrong with setting trade date. {e}")

    def set_filename(self):
        try:
            self.filename: str = f"bhav_copy_{self.trade_date}.csv"
        except Exception as e:
            return (False, f"Something went wrong with setting filename. {e}")

    def set_path(self):
        try:
            self.path: str = "/home/sundaram/ICode/tradingJournal/"
        except Exception as e:
            return (False, f"Something went wrong with setting path. {e}")

    def set_file(self):
        try:
            self.file: str = os.path.join(self.path, self.filename)
        except Exception as e:
            return (False, f"Something went wrong with setting file. {e}")

    def set_old_file_name_to_remove(self):
        try:
            self.old_file_name_to_remove = glob.glob(os.path.join(self.path, "bhav_copy_*.csv"))
        except Exception as e:
            return (False, f"Something went wrong with setting old file. {e}")

    def check_is_bhavcopy(self) -> tuple:
        try:
            if os.path.isfile(self.filename):
                return (True, None)
            else:
                return self.check_market_status()
        except Exception as e:
            return (False, f"something went wrong with check is bhavcopy method: {e}")

    def check_market_status(self) -> tuple:
        try:
            if self.data["marketStatus"] == "Closed":
                return self.get_bhav_copy(self.trade_date)
            else:
                return (True, None)
        except Exception as e:
            return (False, f"something went wrong with check market status: {e}")

    def get_bhav_copy(self, date):
        day: str = date.strftime("%d")
        month: str = date.strftime("%b").upper()
        year: int = date.year
        downloaded_filename = f"cm{day}{month}{year}bhav.csv"

        url = (
            f"https://archives.nseindia.com/content/historical/EQUITIES/{year}/{month}/cm{day}{month}{year}bhav.csv.zip"
        )
        try:
            response_2 = requests.get(url, headers=self.headers)
            time.sleep(5)
        except Exception as e:
            return (False, f"something went wrong with response2. {e}")

        try:
            with zipfile.ZipFile(io.BytesIO(response_2.content), "r") as zip_ref:
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_ref.extractall(temp_dir)
                    extracted_files = os.listdir(temp_dir)
                    # Check that the extracted file is present in the temp directory
                    try:
                        if not extracted_files:
                            return (False, f"No files extracted from the zip")
                        elif downloaded_filename not in extracted_files:
                            return (False, f"{downloaded_filename} not found in the extracted files")
                    except Exception as e:
                        return (False, f"something went wrong with in if not extracted files block: {e}")
                    try:
                        # Rename the file in the temp directory
                        os.rename(os.path.join(temp_dir, downloaded_filename), os.path.join(temp_dir, "temp.csv"))

                        # Move the renamed file to the expected location
                        shutil.move(os.path.join(temp_dir, "temp.csv"), os.path.join(os.getcwd(), self.filename))

                    except Exception as e:
                        return (False, f"Error renaming or moving file inner_most try: {e}")

                    try:
                        # Remove the old file if it exists
                        if self.old_file_name_to_remove:
                            old_file = self.old_file_name_to_remove[0]
                            os.remove(old_file)
                            return (True, None)
                    except Exception as e:
                        return (False, f"Error removing old file: {e}")
        except Exception as e:
            return (False, f"Error renaming or moving file. outer_try: {e} Or file may not be available at nse.")


# ----------------Get Previous Close of the stock--------------------------------
class PreviousClose:
    print()
    print("this is previous close class")
    print()

    def __init__(self) -> None:
        self.fname = glob.glob("*.csv")
        self.filename = self.fname[0]
        self.not_found_in_bhavcopy = ""

    def my_prev_close(self, symbol):
        self.symbol = symbol
        self.pattern = r"\b{}\b".format(re.escape(self.symbol))

        # symb = chk_special(symbol)
        try:
            with open(self.filename, "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_reader)

                for line in csv_reader:
                    if re.search(self.pattern, line[0]) and line[1] == "EQ":
                        return float(line[5])
                    elif re.search(self.pattern, line[0]) and line[1] == "GB":
                        return float(line[5])
                else:
                    self.not_found_in_bhavcopy = self.symbol

            bo_symb = f"{self.not_found_in_bhavcopy}.BO"
            obj = yf.Ticker(bo_symb)
            data = obj.history(period="id")
            return data["Close"][0]

        except Exception as e:
            flash(f"Something went wrong {self.symbol} in my_prev_close(). error: {e}", category="danger")
            return False

    def get_high_low(self, symbol):
        self.pattern = r"\b{}\b".format(re.escape(symbol))

        try:
            with open(self.filename, "r") as csv_file:
                csv_reader = csv.reader(csv_file)
                next(csv_file)

                for line in csv_reader:
                    if re.search(self.pattern, line[0]) and line[1] == "EQ":
                        high = line[3]
                        low = line[4]

                        return (high, low)
                    elif re.search(self.pattern, line[0]) and line[1] == "GB":
                        high = line[3]
                        low = line[4]
                        

                        return (high, low)
                    else:
                        self.not_found_in_bhavcopy = symbol

            bo_symb = f"{self.not_found_in_bhavcopy}.BO"
            obj = yf.Ticker(bo_symb)
            data = obj.history(period="id")
            high = data["HIGH"][0]
            low = data["LOW"][0]
            
            return (high, low)

        except Exception as e:
            flash(f"Something went wrong {symbol} in my_prev_close(). error: {e}", category="danger")
            return (False, False)


# ----------------Stock Search---------------#
class SymbolLookup(PreviousClose):
    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        return f"<class 'SymbolLookup'>"

    def find_symbol(self, symbol) -> bool:
        self.symbol = symbol
        self.pattern = r"\b{}\b".format(re.escape(self.symbol))

        with open(self.filename, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)

            for column in csv_reader:
                if re.search(self.pattern, column[0]):
                    return True
                else:
                    continue
            else:
                self.not_found_in_bhavcopy = self.symbol

                if self.find_symbol_in_yfinance():
                    return True
                else:
                    return False

    def find_symbol_in_yfinance(self) -> bool:
        bo_symb = f"{self.not_found_in_bhavcopy}.BO"
        stock_symb = yf.Ticker(bo_symb)
        df = stock_symb.history(period="id")
        if df.empty:
            return False
        else:
            return True


# Function checks if the string
# contains any ampersand character
def chk_special(string):
    for esc in string:
        # if found it would replace it
        if esc == "&":
            result = string.replace("&", "_")
            return result
        elif esc == "_":
            result = string.replace("_", "&")
            return result

    return string


app.jinja_env.globals.update(PreviousClose=PreviousClose)


# ----------------------------- Logic to display the date of previous close on html page------------------
def bhavcopy_date() -> str:
    fname = glob.glob("*.csv")
    filename = fname[0]
    try:
        with open(filename, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Get the first row

            for line in csv_reader:
                return f"# Current Price and Current Value is as per closing rate of {line[10]}"

    except Exception as e:
        flash(f"Something went wrong in my_prev_close(). error: {e}", category="danger")
        return False


app.jinja_env.globals.update(bhavcopy_date=bhavcopy_date)


def calculate_page_range(current_page, total_pages):
    start_range = max(current_page - 2, 1)
    end_range = min(current_page + 2, total_pages)
    return range(start_range, end_range + 1)


app.jinja_env.globals.update(calculate_page_range=calculate_page_range)
