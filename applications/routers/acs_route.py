import csv
import glob
from flask import jsonify
from flask_login import current_user, login_required

from applications import app
from applications.models import Transactions, Brokers, Research


@app.route("/ac_search", methods=["GET", "POST"])
@login_required
def symbols_dict():
    res = Transactions.query.filter(Transactions.user_id == current_user.id).all()
    list_of_symbols = [r.as_dict() for r in res]
    return jsonify(list_of_symbols)


@app.route("/acs_traders", methods=["GET", "POST"])
@login_required
def trade_code_dict():
    res = Brokers.query.filter(Brokers.user_id == current_user.id).all()
    list_of_trading_code = [r.as_dict() for r in res]
    return jsonify(list_of_trading_code)

@app.route("/acs_research_symb", methods=["GET", "POST"])
@login_required
def research_symb_dict():
    
    res = Research.query.filter(Research.user_id == current_user.id).all()
    list_of_research_symb = [r.as_dict() for r in res]
    return jsonify(list_of_research_symb)

@app.route("/acs_analysts", methods=["GET", "POST"])
@login_required
def analysts_dict():
    res = Research.query.\
    filter(Research.user_id == current_user.id).\
    group_by(Research.analyst).all()

    list_of_analysts = [r.analyst_dict() for r in res]
    return jsonify(list_of_analysts)

@app.route("/acs_bhavcopy_symb", methods=["GET", "POST"])
@login_required
def bhavcopy_symb_dict():
    
    symbols = []
    file_pattern = "bhav_copy_*.csv"

    matching_files = glob.glob(file_pattern)

    if matching_files:
        file_path = matching_files[0]
        with open(file_path, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)

            for row in csv_reader:
                if row[1] == "EQ" or row[1] =="GB":
                    symbols.append(row[0])
    return jsonify(symbols)


    