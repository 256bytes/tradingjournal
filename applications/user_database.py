
from __future__ import annotations
from flask import request
from flask_login import current_user
from sqlalchemy import func, case


from applications.models import Brokers, Transactions, Funds, Research, Analysts
from applications.database import db

class GetUserData:

    def __init__(self, **kwargs) -> None:
        self.route = kwargs.get("route")
        self.user_id = kwargs.get("user_id")
        self.trading_code = kwargs.get("trading_code")
        self.broker_name = (
            db.session.query(Brokers.name)
            .filter(Brokers.trading_code == self.trading_code, Brokers.user_id == self.user_id)
            .first()
        )
        self.symbol = kwargs.get("symbol")
        self.call_type = kwargs.get("call_type")
        self.price = kwargs.get("price")
        self.qty = kwargs.get("qty")
        self.trade_mode = kwargs.get("trade_mode")

    def __str__(self) -> str:
        return f"""
            {self.route}
            {self.user_id}
            {self.trading_code}
            {self.broker_name}
            {self.symbol}
            {self.call_type}
            {self.price}
            {self.qty}
            {self.trade_mode}
        """

    def __repr__(self) -> str:
        return "<class 'GetUserData'>"
    #===========================================================================================
    # ------------------ Start of getting brokerage and taxes ----------------------------------
    def brokerage_and_taxes(self):
        from applications.calc_taxes.get_taxes import CalculateBrokerageAndTaxes

        try:
            self.brokerage_taxes = CalculateBrokerageAndTaxes(
                self.trading_code, self.user_id, self.price, self.qty, self.call_type
            )
            return (True, None)
        except Exception as e:
            return (False, f"Something went wrong while calculating brokerage and taxes. error: {e}")
    # ------------------End of getting brokerage and taxes -----------------------------------
    
    #===========================================================================================
    # ------------------Start Updating Broker's table -----------------------------------

    def add_broker_details(self, user_id, broker_id, trading_code):
        self.broker_id = broker_id
        self.user_id = user_id
        self.trading_code = trading_code.upper()

        # Get details of selected broker from List of Broker table
        from .models import Brokers, List_of_brokers

        broker_details = db.session.query(List_of_brokers).filter(List_of_brokers.id == self.broker_id).first()

        if broker_details:
            try:
                add_broker = Brokers(
                    user_id=self.user_id,
                    name=broker_details.name,
                    trading_code=self.trading_code,
                    broker_type=broker_details.broker_type,
                    equity_delivery=broker_details.equity_delivery,
                    equity_intraday=broker_details.equity_intraday,
                    transaction_chgs=broker_details.transaction_chgs,
                    dp_chgs=broker_details.dp_chgs,
                )
                db.session.add(add_broker)
                db.session.commit()
                return (True, f"{broker_details.name} and trading code {self.trading_code} successfully added.")
            except Exception as e:
                return (False, f"Something went wrong with broker table.{e}")
        else:
            return (False, f"Something went wrong fetching list of broker table.")

    # ------------------End of Updating Broker's table -----------------------------------

    # -----------------Start of validate seller qty -----------------
    # Checking if user has the said quantity of shares with said broker
    def validate_seller_qty(self):
        if self.qty <= 0:
            return (False, "Quantity must be greater than zero")
        else:
            total_shares = self.get_qty()
            if (total_shares) <= 0:
                return (
                    False,
                    f"You do not have any {self.symbol} shares with {self.trading_code} Try with other account\s",
                )
            elif self.qty > (total_shares):
                return (False, f"Maximum shares you can sell is: {total_shares} from {self.trading_code} account")
            else:
                self.qty = self.qty * -1
                return (True, None)

    def get_qty(self):
        total_shares = (
            db.session.query(func.sum(Transactions.qty).label("total_qty"))
            .filter(
                Transactions.user_id == self.user_id,
                Transactions.trading_code == self.trading_code,
                Transactions.script == self.symbol,
                Transactions.type == "CNC",
            )
            .group_by(Transactions.trading_code)
            .first()
        )
        return total_shares.total_qty

    # ------------------- End of validate seller qty ----------------------

    # ------------------- Start of update analysts ------------------------

    def update_analyst(self, analyst) -> bool:
        from applications.models import Analysts

        self.analyst = analyst
        # --- Check whether the analyst is already present or not--------

        get_analyst = Analysts.query.filter(Analysts.name == self.analyst).first()
        try:
            if not get_analyst:
                add_analyst = Analysts(
                    name=self.analyst, number_of_calls=1, target_achieved=0, stop_loss_triggered=0, performance=0.00
                )
                db.session.add(add_analyst)
                db.session.commit()
                return (True, f"successful!")
            else:
                get_analyst.number_of_calls += 1
                db.session.commit()
                return (True, f"successful!")
        except Exception as e:
            return (False, f"Something went wrong in analyst table. {e}")

    # ------------------- End of update analysts ------------------------

    # ------------------- Start of update research ------------------------

    def update_research(self, stop_loss, target, call_validity, analyst, resource) -> bool:
        self.stop_loss = stop_loss
        self.target = target
        self.call_validity = call_validity
        self.analyst = analyst
        self.resource = resource
        from applications.models import Research

        try:
            db.session.rollback()
            db.session.begin()
            add_research = Research(
                user_id=self.user_id,
                script=self.symbol,
                price=self.price,
                call=self.call_type,
                stop_loss=self.stop_loss,
                target=self.target,
                call_validity=self.call_validity,
                analyst=self.analyst,
                resource=self.resource,
            )
            db.session.add(add_research)
            db.session.commit()
            return (True, f"Transaction of your analysis was successfully added to your analytics.")

        except Exception as e:
            return (False, f"Something went wrong while adding to research table. {e}")

    # ------------------- End of update research ------------------------

    # ------------------- Start of update research_tgt_sl Column ------------------------
    def update_tgt_sl_column_research(self, row_id, call_validity, analyst_name, tgt_sl):
        self.row_id = row_id
        self.call_validity = call_validity
        self.analyst_name = analyst_name
        self.tgt_sl = tgt_sl
        try:
            from applications.models import Research

            get_tgt_sl_status = (
                db.session.query(Research)
                .filter(
                    Research.user_id == self.user_id,
                    Research.call_validity == self.call_validity,
                    Research.analyst == self.analyst_name,
                    Research.script == self.symbol,
                )
                .first()
            )

            get_tgt_sl_status.tgt_sl = self.tgt_sl
            db.session.commit()
            return (True, None)
        except Exception as e:
            return (False, f"Something went wrong with update tgt sl column. {e}")

    # ------------------- End of update research_tgt_sl Column ------------------------
    # ------------------- Start of get call data from Research table ------------------------
    def get_call_data(self):
        tc = db.session.query(
            func.count(Research.tgt_sl).label("total_calls")
        ).filter(
            Research.user_id == self.user_id
        ).first()

        t_open = db.session.query(
            func.count(Research.tgt_sl).label("total_open")
        ).filter(
            Research.user_id == self.user_id,\
            Research.tgt_sl == "open"
        ).first()

        t_live = db.session.query(
            func.count(Research.tgt_sl).label("total_live")
        ).filter(
            Research.user_id == self.user_id,\
            Research.tgt_sl == "live"
        ).first()

        t_close = db.session.query(
            func.count(Research.tgt_sl).label("total_closed")
        ).filter(
            Research.user_id == self.user_id,\
            Research.tgt_sl.in_(["target", "stoploss"])
        ).first()

        return tc.total_calls, t_open.total_open, t_live.total_live, t_close.total_closed
    # ------------------- End of get call data from Research table ------------------------
    # ------------------- Start of get analyst call data from Research table ------------------------
    def get_analyst_call_data(self, analyst):

        tc = db.session.query(
            Analysts.number_of_calls
        ).filter(
            Analysts.name == analyst
        ).first()

        t_open = db.session.query(
            func.count(Research.tgt_sl).label("total_open")
        ).filter(
            Research.analyst == analyst,\
            Research.tgt_sl == "open"
        ).first()

        t_live = db.session.query(
            func.count(Research.tgt_sl).label("total_live")
        ).filter(
            Research.analyst == analyst,\
            Research.tgt_sl == "live"
        ).first()

        t_target = db.session.query(
            Analysts
        ).filter(
            Analysts.name == analyst
        ).first()

        t_sl = db.session.query(
             Analysts
        ).filter(
            Analysts.name == analyst
        ).first()
        t_closed = (t_target.target_achieved + t_sl.stop_loss_triggered)
 
        return tc.number_of_calls, t_open.total_open, t_live.total_live,t_target.target_achieved, t_closed

    # ------------------- End of get analyst call data from Research table ------------------------
    # ------------------- Start of update analyst table ------------------------
    def update_sl_tgt_analyst_tabl(self, analyst_name, option):
        self.analyst_name = analyst_name
        self.option = option
        # self.symbol = symbol
        # self.row_id = row_id
        # self.date = date

        try:
            from applications.models import Analysts

            get_analyst_data = db.session.query(Analysts).filter(Analysts.name == self.analyst_name).first()
            
            if self.option == "target":
                get_analyst_data.target_achieved += 1
                db.session.commit()
                if get_analyst_data.target_achieved <= 0:
                    pass
                else:
                    total_closed_calls = int((get_analyst_data.target_achieved + get_analyst_data.stop_loss_triggered))
                    performance = round(
                        ((get_analyst_data.target_achieved / total_closed_calls) * 100), 2
                    )
                    get_analyst_data.performance = performance
                    db.session.commit()
                    return (True, None)
            else:
                get_analyst_data.stop_loss_triggered += 1
                db.session.commit()
                if get_analyst_data.stop_loss_triggered <= 0:
                    pass
                else:
                    total_closed_calls = int((get_analyst_data.target_achieved + get_analyst_data.stop_loss_triggered))
                    performance = round(
                        ((get_analyst_data.target_achieved / total_closed_calls) * 100), 2
                    )
                    get_analyst_data.performance = performance
                    db.session.commit()
                    return (True, None)
        except Exception as e:
            return (False, f"something went wrong with update analyst table. {e}")

    # ------------------- End of update analyst table ------------------------

    # ------------------ Start of withdraw funds ---------------------------

    def withdraw_fund(self, withdrawal_amt):
        self.withdrawal_amt = withdrawal_amt

        try:
            payout_fund = Funds(user_id=self.user_id, trading_code=self.trading_code, pay_out=self.withdrawal_amt)
            db.session.add(payout_fund)
            db.session.commit()
            return (True, f"{self.withdrawal_amt} withdrawn from {self.trading_code} account")
        except Exception as e:
            return (False, f"Something went wrong with payout. {e}")

    # ------------------ End of withdraw funds ---------------------------

    # ------------------ Start of update funds ---------------------------

    def update_funds(self) -> tuple:
        if self.call_type == "Buy":
            debit_col = "debits"
            credit_col = "credits"
            debit_value = self.brokerage_taxes.r_payable
            credit_value = None
        else:
            debit_col = "debits"
            credit_col = "credits"
            debit_value = None
            credit_value = self.brokerage_taxes.r_payable
        try:
            db.session.rollback()
            db.session.begin()
            update_funds_tbl = Funds(
                user_id=current_user.id,
                trading_code=self.trading_code,
                **{debit_col: debit_value, credit_col: credit_value},
            )
            db.session.add(update_funds_tbl)
            db.session.commit()
            return (True, None)
        except Exception as e:
            return (False, f"something went wrong with update funds. error: {e}")

    # ------------------ End of update funds ---------------------------
    # ------------------ Start of Add funds ---------------------------

    def add_funds(self, add_fund) -> tuple:
        self.add_fund = add_fund
        try:
            add_funds = Funds(
                user_id=self.user_id,
                trading_code=self.trading_code,
                pay_in=self.add_fund,
            )
            db.session.add(add_funds)
            db.session.commit()
            return (True, None)
        except Exception as e:
            return (False, f"something went wrong while adding the fund. {e}")

    # ------------------ End of Add funds ----------------------------------------
    # ------------------ Start of Update_balance funds ---------------------------
    def update_balance(self, fund_bal):
        self.fund_bal = fund_bal
        try:
            fund_detail = (
                db.session.query(Funds)
                .filter(Funds.user_id == self.user_id, Funds.trading_code == self.trading_code)
                .order_by(Funds.id.desc())
                .first()
            )
            print()
            print(f"pay in: {fund_detail.pay_in}")
            print(f"credits: {abs(fund_detail.credits)}")
            print(f"pay out: {fund_detail.pay_out}")
            print(f"debits: {fund_detail.debits}")
            print(f"fund bal: {self.fund_bal}")
            print()
            new_bal = round(float((
                (fund_detail.pay_in + abs(fund_detail.credits))
                - (fund_detail.pay_out + fund_detail.debits)
                + self.fund_bal
            )),2)
            print()
            print(f"new balance = {new_bal}")
            print()
            if new_bal == 0:
                fund_detail = 0.00
                db.session.commit()
                return (True, f"Successfully updated the funds table.")

            else:
                fund_detail.balance = new_bal
                db.session.commit()
                return (True, f"Successfully updated the funds table.")
        except Exception as e:
            return (False, f"something went wrong while updating the balance. {e}")

    # ------------------ End of Update_balance funds ---------------------------

    # ------------------ Start of Get balance ---------------------------
    def get_balance(self):
        try:
            fund_detail = (
                db.session.query(Funds)
                .filter(Funds.user_id == self.user_id, Funds.trading_code == self.trading_code)
                .order_by(Funds.id.desc())
                .first()
            )
            if fund_detail:
                return (True, float(fund_detail.balance))
            else:
                return (True, 0.00)
        except Exception as e:
            return (False, f"something went wrong with get balance. {e}")

    # ------------------ End of Get balance ---------------------------

    # ------------------ Start of get sl/tgt status ---------------------------
    def get_tgt_sl_status(self, row_id, call_validity, analyst_name):
        self.row_id = row_id
        self.call_validity = call_validity
        self.analyst_name = analyst_name

        from applications.models import Research

        try:
            tgt_sl_status = (
                db.session.query(Research.tgt_sl)
                .filter(
                    Research.user_id == self.user_id,
                    Research.call_validity == self.call_validity,
                    Research.analyst == self.analyst_name,
                    Research.script == self.symbol,
                )
                .first()
            )

            return (True, f"success")
        except Exception as e:
            return (False, f"Something went wrong with get tgt sl status. {e}")

    # ------------------ End of get sl/tgt status ---------------------------

    # ------------------ Start of add transactions ---------------------------

    def add_transactions(self) -> None:
        if self.call_type == "Buy":
            self.qty = int(self.qty)
            self.brokerage_taxes.r_payable = float(self.brokerage_taxes.r_payable)
        elif self.call_type == "Sell":
            self.qty = -int(self.qty)
            self.brokerage_taxes.r_payable = -float(self.brokerage_taxes.r_payable)
        else:
            self.qty = self.qty

        try:
            db.session.rollback()
            db.session.begin()
            transactions_to_add = Transactions(
                user_id=current_user.id,
                trade_mode=self.trade_mode,
                call=self.call_type,
                script=self.symbol,
                price=self.price,
                qty=self.qty,
                brokerage_per_unit=self.brokerage_taxes.r_b,
                total_brokerage=self.brokerage_taxes.r_tb,
                net_rate_per_unit=self.brokerage_taxes.r_rpu,
                net_total_before_levies=self.brokerage_taxes.r_net_before_tax,
                transaction_chgs=self.brokerage_taxes.r_tchgs,
                dp_chgs=self.brokerage_taxes.r_dp_chgs,
                stt=self.brokerage_taxes.r_stt,
                sebi_turnover_fees=self.brokerage_taxes.r_sebi,
                stamp_duty=self.brokerage_taxes.r_sd,
                gst=self.brokerage_taxes.r_gst,
                total_taxes=self.brokerage_taxes.r_total_taxes_without_brokerage,
                net_total=self.brokerage_taxes.r_payable,
                broker=self.broker_name.name,
                trading_code=self.trading_code,
            )
            db.session.add(transactions_to_add)
            db.session.commit()
            return (True, "Transactions was successful")
        except Exception as e:
            return (False, f"Something went wrong while inserting the data to the transaction table. error: {e}")

    # ------------------ End of add transactions ---------------------------
    # ------------------ Start of delete User ---------------------------
    def delete_my_account(self):
        from applications.models import Transactions, Research, Funds, Brokers, Users

        try:
            Transactions.query.filter_by(user_id=self.user_id).delete()
            Research.query.filter_by(user_id=self.user_id).delete()
            Funds.query.filter_by(user_id=self.user_id).delete()
            Brokers.query.filter_by(user_id=self.user_id).delete()
            account_to_delete = Users.query.filter_by(id=self.user_id).first()
            db.session.delete(account_to_delete)
            db.session.commit()
            return (True, f"Account successfully deleted!")

        except Exception as e:
            return (False, f"Something went wrong error: {e}")

    # ------------------ End of delete User ---------------------------
    # ------------------ Start of delete Broker ---------------------------
    def delete_my_broker_account(self):
        from applications.models import Transactions, Brokers, Funds
        try:
            Transactions.query.filter_by(
                user_id = self.user_id,\
                trading_code = self.trading_code
            ).delete()

            Brokers.query.filter_by(
                user_id = self.user_id,\
                trading_code = self.trading_code
            ).delete()

            Funds.query.filter_by(
                user_id = self.user_id,\
                trading_code = self.trading_code
            ).delete()
            db.session.commit()

            return (True, f"successfully deleted")
        except Exception as e:
            return (False, f"something went wrong while deleting broker account. {e}")


    # ------------------ End of delete Broker -----------------------------
    # ------------------ Start of generate invoice ---------------------------

    def generate_buy_data(self):
        try:
            buy_transac_details = (
                db.session.query(Transactions)
                .filter(
                    Transactions.user_id == self.user_id,
                    Transactions.trading_code == self.trading_code,
                    Transactions.script == self.symbol,
                    Transactions.call == "Buy",
                )
                .all()
            )

            return (True, buy_transac_details)
        except Exception as e:
            return (False, f"Something went wrong with generate invoice method: {e}")

    def generate_sell_data(self):
        try:
            sell_transac_details = (
                db.session.query(Transactions)
                .filter(
                    Transactions.user_id == self.user_id,
                    Transactions.trading_code == self.trading_code,
                    Transactions.script == self.symbol,
                    Transactions.call == "Sell",
                )
                .all()
            )

            return (True, sell_transac_details)
        except Exception as e:
            return (False, f"Something went wrong with generate invoice method: {e}")

    # ------------------ End of generate invoice ---------------------------
    # ------------------ Start of Broker wise pl data ---------------------------
    def get_broker_wise_pl_data(self):
        i_itr = 1
        j_itr = 1
        holdings = []
        data = db.session.query(
            Transactions.trading_code
        ).filter(
            Transactions.user_id == self.user_id,\
            Transactions.trade_mode == "CNC"
        ).distinct()

        for i in data:
            net_p_L = 0.00
            same_tc: bool 
            # print(f"start of i loop: {i.trading_code} --- iteration: {i_itr}")
            # print()
            # print(i)
            # print(i.trading_code)
            # print()
            subquery = db.session.query(
                Transactions.script,
                db.func.min(Transactions.id).label("min_id")
            ).filter(
                Transactions.user_id == self.user_id,\
                Transactions.trading_code == i.trading_code,\
                Transactions.trade_mode == "CNC"
            ).group_by(Transactions.script).subquery()

            data = db.session.query(
                Transactions
            ).join(
                subquery,
                Transactions.id == subquery.c.min_id
            ).all()
            data_count = len(data)
            loop_len = data_count
            for j in data:
                
                # print()
                # print(f"this is j: {j}")
                # print(f"this is j trading code: {j.trading_code}")
                # print(f"this is j.script: {j.script}")
                # print()
                broker_name, trading_code, net_profit_loss,\
                same_tc = get_broker_pl(
                    user_id = j.user_id,\
                    trading_code = j.trading_code,\
                    script = j.script,\
                    loop_len = data_count
                    # p_l = net_p_L
                )
                # print(f"{net_p_L} + {net_profit_loss} = {net_p_L + net_profit_loss}")
                net_p_L += net_profit_loss
                # print(f"This net p L after the return from Callee: {net_p_L}")
                # print()
                # print(f"this is same tc from caller: {same_tc}")
                # print(trading_code)
                # print()
                # print(f"this is data count: {data_count}")
                # print(f"loop len: {loop_len}")
                loop_len -= 1
                # print(f"loop len: {loop_len}")
                if trading_code is None:
                    continue
                if loop_len != 0:
                    continue
                
                # print()
                # print(f"this is net pL from the caller: {net_p_L}")
                # print()
                filtered_data = {}
                filtered_data["broker_name"] = broker_name
                filtered_data["trading_code"] = trading_code
                filtered_data["net_profit_loss"] = net_p_L
                holdings.append(filtered_data)

                # print(f"this is data count: {data_count}")
                # print(f"loop len: {loop_len}")
                i_itr += 1
        # print(f"End of i loop: {i.trading_code}")
        # i_itr = 1
        # j_itr = 1
            # data = db.session.query(
            #     Transactions
            # ).join(
            #     subquery,
            #     Transactions.id == subquery.c.min_id
            # ).all()

            # for i in data:

        return (True, holdings)
        return (False, f"Something went wrong with broker_wise_pl_data: {e}")

    # ------------------ End of Broker wise pl data ---------------------------
    # ===========================================================================================
    # ------------------ Start of Get all Research Data ---------------------------
    def get_all_research_data(self):
        try:
            page = request.args.get('page', 1, int)
            data = Research.query.filter(Research.user_id == self.user_id).\
                                                    order_by(Research.date.desc()).\
                                                        paginate(page=page, per_page=5)
    
            
            ad = db.session.query(Analysts).all()
            holdings = []

            for i in data:
                
                sum_qty = db.session.query(func.sum(Transactions.qty).label("holding")).\
                    filter(Transactions.user_id == self.user_id, Transactions.script == i.script).\
                    first()
                holdings.append(sum_qty.holding)

            return (True, data, ad, holdings)

        except Exception as e:
            return(False, f"Something went wrong while fetching research table: {e}")
    
    # ------------------ End of Get all Research Data ---------------------------
    # ------------------ Start of Script wise Research Data ---------------------------
    def get_script_wise_research_data(self):
        try:
            data = (
                db.session.query(Research)
                .filter(Research.user_id == self.user_id, Research.script == self.symbol)
                .all()
            )
            
            ad = db.session.query(Analysts).all()
            
            holdings = []

            for i in data:
                sum_qty = (
                    db.session.query(func.sum(Transactions.qty).label("holdings"))
                    .filter(Transactions.user_id == self.user_id, Transactions.script == i.script)
                    .first()
                )
                holdings.append(sum_qty.holdings)
            return (True, data, ad, holdings)
        except Exception as e:
            return (False, f"Something went wrong while fetching data from Research table: {e}", None, None, None)

    # ------------------ End of Script wise Research Data -----------------------------------
    # ===========================================================================================
    # ------------------ Start of Analyst wise Research Data -----------------------------------
    def get_analyst_wise_research_data(self, analyst):
        self.analyst = analyst
        try:

            page = request.args.get("page", 1, int)
            data = (
                db.session.query(Research)
                .filter(Research.user_id == self.user_id, Research.analyst == self.analyst)
                .order_by(Research.date.desc())
                .paginate(page=page, per_page=5)
            )

            ad = db.session.query(Analysts).all()
            holdings = []

            for i in data:
                sum_qty = (
                    db.session.query(func.sum(Transactions.qty).label("holdings"))
                    .filter(Transactions.user_id == self.user_id, Transactions.script == i.script)
                    .first()
                )
                holdings.append(sum_qty.holdings)

            return (True, data, ad, holdings)
        except Exception as e:
            return (False, f"Something went wrong while fetching for analyst wise research: {e}", None, None)

    # ------------------ End of Analyst wise Research Data -----------------------------------
    # ===========================================================================================
    # ------------------ Start of Open call data -----------------------------------
    def get_all_open_calls(self):
        try:
            
            page = request.args.get("page", 1, int)
            data = (
                db.session.query(Research)
                .filter(Research.user_id == self.user_id, Research.tgt_sl == "live")
                .order_by(Research.id.desc()).paginate(page=page, per_page=5)
                
            )

            ad = db.session.query(Analysts).all()
            holdings = []

            for i in data:
                sum_qty = (
                    db.session.query(func.sum(Transactions.qty).label("holdings"))
                    .filter(Transactions.user_id == self.user_id, Transactions.script == i.script)
                    .first()
                )

                holdings.append(sum_qty.holdings)

            return (True, data, ad, holdings)
        except Exception as e:
            return (False, f"Something went wrong while fetching open calls: {e}", None, None)

    # ------------------ End of Open call data -----------------------------------
    # ===========================================================================================
    # ------------------ Start of Validating the quantity to sell ---------------------------

    def validate_qty_to_sell(self, qty_to_sell):
        try:
            data = (
                db.session.query(func.sum(Transactions.qty).label("net_qty"))
                .filter(
                    Transactions.user_id == self.user_id,
                    Transactions.trading_code == self.trading_code,
                    Transactions.script == self.symbol,
                )
                .first()
            )
            for x in data:
                if x >= qty_to_sell:
                    return (True, data)
                else:
                    return (False, f"Maximum Shares you can sell from {self.trading_code} Account is {x}")

        except Exception as e:
            return (False, f"Something went wrong while fetching validate qty to sell: {e}")

    # ------------------ End of Validating the quantity to sell ---------------------------
    
    # ------------------ Start of Get Invested Value ---------------------------
    def get_invested_value(self):
        from applications.helpers import PreviousClose

        inv_value: float = 0.00
        if self.user_id and self.trading_code:
            try:
                holdings = (
                    db.session.query(
                    Transactions.script,
                    func.sum(Transactions.qty).label("net_qty"),
                    func.sum(Transactions.net_total).label("total_investments"),
                    ).\
                    filter(
                    Transactions.user_id == self.user_id,
                    Transactions.trading_code == self.trading_code
                    ).\
                    group_by(Transactions.script)
                )
                for hld in holdings:
                    pcp = PreviousClose().my_prev_close(hld.script)
                    curr_value = pcp * hld.net_qty
                    inv_value += curr_value

                return (True, inv_value)
            
            except Exception as e:
                return (False, f"something went wrong while fetching get invested value (borker wise) block: {e}")

        else:
            try:
                holdings = (
                    db.session.query(
                        Transactions.script,
                        func.sum(Transactions.qty).label("net_qty"),
                        func.sum(Transactions.net_total).label("total_investments"),
                    )
                    .filter(Transactions.user_id == self.user_id, Transactions.trade_mode == "CNC")
                    .group_by(Transactions.script)
                )

                for hld in holdings:
                    pcp = PreviousClose().my_prev_close(hld.script)
                    curr_value = pcp * hld.net_qty
                    inv_value += curr_value

                return (True, inv_value)
            except Exception as e:
                return (False, f"something went wrong while fetching get invested value block: {e}")

    # ------------------ End of Get Invested Value ---------------------------
    # ------------------ Start of Get Total Scrips ---------------------------
    def get_total_scrips(self):
        trading_code = self.trading_code
        total_scrips = 0

        try:
            if not trading_code:
                data = db.session.query(
                    Transactions.script
                ).filter(
                    Transactions.user_id == self.user_id,\
                    Transactions.trade_mode == "CNC"
                ).distinct()

                for i in data:
                    data_2 = db.session.query(
                        func.sum(Transactions.qty).label("net_qty")
                    ).filter(
                        Transactions.user_id == self.user_id,\
                        Transactions.script == i.script,\
                        Transactions.trade_mode == "CNC"
                        
                    ).all()
                    for j in data_2:
                        if j.net_qty > 0:
                            
                            total_scrips += 1
                            print()
                            print(i.script)
                            print(total_scrips)
                            print()
                    # total_qty = 0
                    # buy_qty = 0
                    # sell_qty = 0
                    # for j in data_2:
    
                    #     if j.call == "Buy":
                    #         buy_qty = i.qty
                    #         total_qty += buy_qty
                    #     elif j.call == "Sell":
                    #         sell_qty = i.qty
                    #         total_qty -= sell_qty
                    # if total_qty > 0:
                    #     total_scrips += 1

                return(True, total_scrips)
            else:
                data = db.session.query(
                    Transactions.script
                ).filter(
                    Transactions.user_id == self.user_id,\
                    Transactions.trading_code == trading_code,\
                    Transactions.trade_mode == "CNC"
                ).distinct()

                for i in data:
                    data_2 = db.session.query(
                        func.sum(Transactions.qty).label("net_qty")
                    ).filter(
                        Transactions.user_id == self.user_id,\
                        Transactions.script == i.script,\
                        Transactions.trading_code == trading_code,\
                        Transactions.trade_mode == "CNC"
                        
                    ).all()

                    for j in data_2:
                        if j.net_qty > 0:
                            total_scrips += 1
                return(True, total_scrips)
        except Exception as e:
            return(False, f"something went wrong while counting total scrips: {e}")
    # ------------------ End of Get Total Scrips ---------------------------
    # ------------------ Start of Script Wise P&L ---------------------------
    def get_script_wise_pl(self):
        
        holdings = []
        total_gain_loss = 0.00
        script_wise = True
        data = db.session.query(
            Transactions.script, Transactions.trading_code
        ).filter(
            Transactions.user_id == self.user_id,\
            Transactions.trade_mode == "CNC"
        ).distinct()

        for i in data:
            # print()
            # print(i.script)
            # print(i.trading_code)
            # print()
            trading_code, script, net_profit_loss,\
                 number_of_transactions = get_script_pl(
                user_id = self.user_id, symbol = i.script, trading_code = i.trading_code
            )
            if trading_code is None:
                continue
            total_gain_loss += net_profit_loss

            filtered_data = {}
            filtered_data["trading_code"] = trading_code
            filtered_data["script"] = script
            filtered_data["net_profit_loss"] = net_profit_loss
            filtered_data["number_of_transactions"] = number_of_transactions
            filtered_data["total_gain_loss"] = total_gain_loss
            holdings.append(filtered_data)

        return holdings, total_gain_loss


    # ------------------ End of Script Wise P&L ---------------------------
    
    # -------------------Start of Get Consolidated data for Holdings/Broker_Wise/Script_Wise--------------------------------------------
    def get_consolidated_hld_data(self):
        if self.trading_code == None and self.symbol == None:
            all_data = True
            holdings = []
            data = db.session.query(
                Transactions.script
            ).filter(
                Transactions.user_id == self.user_id,\
                Transactions.trade_mode == "CNC"
                    ).\
                        distinct()

            for i in data:
                net_qty,\
                    avg_cost,\
                        total_investments,\
                            current_price,\
                                current_value,\
                                        = get_script_holding_data(user_id = self.user_id, symbol = i.script, all_data = all_data)

                filtered_data = {}
                
                filtered_data["script"] = i.script
                filtered_data["net_qty"] = net_qty
                filtered_data["avg_cost"] = avg_cost
                filtered_data["total_investments"] = total_investments
                filtered_data["current_price"] = current_price
                filtered_data["current_value"] = current_value
                holdings.append(filtered_data)

            return holdings
        
        elif self.trading_code:
            holdings = []
            trading_code_wise = True
            subquery = db.session.query(
                Transactions.script,
                db.func.min(Transactions.id).label('min_id')
            ).filter(
                Transactions.user_id == self.user_id,
                Transactions.trading_code == self.trading_code,
                Transactions.trade_mode == "CNC"
            ).group_by(Transactions.script).subquery()

            data = db.session.query(Transactions).join(
                subquery,
                Transactions.id == subquery.c.min_id
            ).all()

            for i in data:
                
                date, script, net_qty, avg_cost, total_brokerage,\
                total_taxes, total_investments,\
                    current_price, current_value = get_script_holding_data(
                    user_id = self.user_id, symbol = i.script, trading_code = self.trading_code,
                    trading_code_wise = trading_code_wise
                    )

                filtered_data = {}
                filtered_data["date"] = date
                filtered_data["trading_code"] = i.trading_code
                filtered_data["script"] = script
                filtered_data["net_qty"] = net_qty
                filtered_data["avg_cost"] = avg_cost
                filtered_data["total_brokerage"] = total_brokerage
                filtered_data["total_taxes"] = total_taxes
                filtered_data["total_investments"] = total_investments
                filtered_data["current_price"] = current_price
                filtered_data["current_value"] = current_value
                holdings.append(filtered_data)
            return holdings

        elif self.symbol:
            holdings = []
            script_wise = True
            data = db.session.query(
                Transactions.trading_code, Transactions.script
            ).filter(
                Transactions.user_id == self.user_id,\
                Transactions.script == self.symbol,\
                Transactions.trade_mode == "CNC"
            ).distinct()
                
            for i in data:
                date, broker_name, net_qty, avg_cost,\
                total_brokerage, total_taxes, total_investments,\
                    current_price, current_value = get_script_holding_data(
                        user_id = self.user_id, symbol = self.symbol, trading_code = i.trading_code,
                        script_wise = script_wise
                            )
                filtered_data = {}
                filtered_data["date"] = date
                filtered_data["broker_name"] = broker_name
                filtered_data["trading_code"] = i.trading_code
                filtered_data["script"] = self.symbol
                filtered_data["net_qty"] = net_qty
                filtered_data["avg_cost"] = avg_cost
                filtered_data["total_brokerage"] = total_brokerage
                filtered_data["total_taxes"] = total_taxes
                filtered_data["total_investments"] = total_investments
                filtered_data["current_price"] = current_price
                filtered_data["current_value"] = current_value
                holdings.append(filtered_data)
            return holdings


def get_script_holding_data(**kwargs):

    user_id = kwargs.get("user_id")
    symb = kwargs.get("symbol")
    trading_code = kwargs.get("trading_code")
    all_data = kwargs.get("all_data")
    trading_code_wise = kwargs.get("trading_code_wise")
    script_wise = kwargs.get("script_wise")

    if all_data: # this is to get the all consolidated data of the user.

        data = db.session.query(
            Transactions
        ).filter(
            Transactions.user_id == user_id,\
            Transactions.script == symb,\
        ).all()

        itr = 1
        sum_qty = 0
        net_investment = 0.00
        for y in data:
            # print(f"start of for {y.script} loop---------: {itr}")

            if y.call == "Buy" or y.call == "Bonus":
                sum_qty += y.qty
                net_investment += y.net_total

            elif y.call == "Sell":
                if (sum_qty - abs(y.qty)) == 0:
                    sum_qty = 0
                    net_investment = 0

                else:
                    sum_qty -= abs(y.qty)
                    net_investment -= abs(y.net_total)


            # print()
            # print(y.script)
            # print(sum_qty)
            # print(net_investment)
            # print()
            # print(f"end of for {y.script} loop-----------: {itr}")
            # itr += 1
        # print()
        # print(y.script)
        # print(sum_qty)
        # print(net_investment)
        # print()
        if sum_qty > 0 and net_investment >= 0:
            avg_cost = get_avg_cost(sum_qty, net_investment)
            c_price, c_value = get_current_price_value(y.script, sum_qty)
            return sum_qty, avg_cost,net_investment, c_price, c_value
        
        c_price, c_value = get_current_price_value(y.script, sum_qty)
        return sum_qty, 0.01,0.01, c_price, c_value
    
    elif trading_code and trading_code_wise: # to get the consolidated data of user's trading account wise

        data = db.session.query(
            Transactions
        ).filter(
            Transactions.user_id == user_id,\
            Transactions.script == symb,\
            Transactions.trading_code == trading_code
        ).all()

        itr = 1
        sum_qty = 0
        net_investment = 0.00
        total_brokerage = 0.00
        total_taxes = 0.00

        for y in data:
            # print(f"start of for {y.script} loop---------: {itr}")

            if y.call == "Buy" or y.call == "Bonus":
                sum_qty += y.qty
                net_investment += y.net_total
                total_brokerage += y.total_brokerage
                total_taxes += y.total_taxes

            elif y.call == "Sell":
                if (sum_qty - abs(y.qty)) == 0:
                    sum_qty = 0
                    net_investment = 0.00
                    total_brokerage = 0.00
                    total_taxes = 0.00

                else:
                    sum_qty -= abs(y.qty)
                    net_investment -= abs(y.net_total)
                    total_brokerage += y.total_brokerage
                    total_taxes += y.total_taxes

        if sum_qty > 0 and net_investment >= 0:
            avg_cost = get_avg_cost(sum_qty, net_investment)
            c_price, c_value = get_current_price_value(y.script, sum_qty)
            return y.date, y.script, sum_qty, avg_cost, total_brokerage, total_taxes, net_investment, c_price, c_value
        
        elif sum_qty > 0 and net_investment < 0:
            # print()
            # print(f"net investment < 0: {net_investment}")
            # print()
            net_investment = 0.1
            avg_cost = get_avg_cost(sum_qty, net_investment)
            c_price, c_value = get_current_price_value(y.script, sum_qty)
            # print()
            # print(f"net investment < 0: {net_investment}")
            # print()
            return y.date, y.script, sum_qty, avg_cost, total_brokerage, total_taxes, net_investment, c_price, c_value
        
        c_price, c_value = get_current_price_value(y.script, sum_qty)
        return y.date, y.script, sum_qty, 0.01, 0.01, 0.01, net_investment, c_price, c_value

    elif symb and script_wise:

        data = db.session.query(
            Transactions
        ).filter(
            Transactions.user_id == user_id,\
            Transactions.script == symb,\
            Transactions.trading_code == trading_code
        ).all()
        
        itr = 1
        sum_qty = 0.00
        net_investment = 0.00
        total_brokerage = 0.00
        total_taxes = 0.00
        for y in data:
            if y.call == "Buy" or y.call == "Bonus":

                sum_qty += y.qty
                net_investment += y.net_total
                total_brokerage += y.total_brokerage
                total_taxes += y.total_taxes

            elif y.call == "Sell":

                if (sum_qty - abs(y.qty)) == 0:
                    
                    sum_qty = 0
                    net_investment = 0.00
                    total_brokerage = 0.00
                    total_taxes = 0.00

                    # print(sum_qty)
                    # print(net_investment)
                else:
                    # print()
                    # print(f"else sum_qty != 0 block: {y}--> script: {y.script}")
                    # print()
                    # print()
                    # print(f"script: {y.script} and price: {y.price}")
                    # print()
                    sum_qty -= abs(y.qty)
                    net_investment -= abs(y.net_total)
                    total_brokerage += y.total_brokerage
                    total_taxes += y.total_taxes
                    # print(sum_qty)
                    # print(net_investment)
            # print()
            # print(f"this is from symb and script wise inside the for block: sum qty is:{y}--> {sum_qty} and net_inv: {net_investment}")
            # print()
            # itr += 1
        if sum_qty > 0 and net_investment >= 0:
            # print()
            # print(f"this is from symb and script wise block: sum qty is: {sum_qty} and net_inv: {net_investment}")
            # print()
            avg_cost = get_avg_cost(sum_qty, net_investment)
            c_price, c_value = get_current_price_value(y.script, sum_qty)
            return y.date, y.broker, sum_qty, avg_cost, total_brokerage, total_taxes, net_investment, c_price, c_value
        c_price, c_value = get_current_price_value(y.script, sum_qty)
        return y.date, y.broker, sum_qty, 0.01, 0.01, 0.01, net_investment, c_price, c_value


#-------Functions----------------------------
def get_avg_cost(sum_qty, net_investment):

    default_cost = 0.01
    if sum_qty <= 0:
        return default_cost
    else:
        avg_cost = net_investment/sum_qty
        if avg_cost <= 0:
            return default_cost
        return avg_cost
        
def get_current_price_value(symbol, sum_qty):
        
    from applications.helpers import PreviousClose
    prev_close = PreviousClose()
    last_close = prev_close.my_prev_close(symbol)
    current_price = last_close
    current_value = current_price*sum_qty

    return current_price, current_value

def get_script_pl(**kwargs):

    user_id = kwargs.get("user_id")
    symb = kwargs.get("symbol")
    trading_code = kwargs.get("trading_code")
    
    data = db.session.query(
        Transactions
    ).filter(
        Transactions.user_id == user_id,\
        Transactions.script == symb,\
        Transactions.trading_code == trading_code
    ).all()

    itr = 1
    tr = 0 # counter for number of buy-sell transactions
    buy_qty = 0
    sell_qty = 0
    sum_qty = 0
    total_investments = 0.00
    net_pro_loss = 0.00
    net_selling_cost = 0.00
    buy_sell = False
    for y in data:
        # print()

        # print(f"start of for {y.script} loop---------: {itr}")
        # print(f"call:   loop---------: {y.call}")

        if y.call == "Buy":
            buy_qty = y.qty
            sum_qty += buy_qty
            total_investments += y.net_total
            # print()
            # print(f"from buy: sum qty: {sum_qty}")
            # print(f"from buy: y.net_total: {y.net_total}")
            # print(f"from buy: total_investments: {total_investments}")
            # print()
        elif y.call == "Sell":
            sell_qty = abs(y.qty)
            sum_qty -= sell_qty
            if sum_qty == 0:

                # print(f"from sell = 0: net_pro_loss: {net_pro_loss}")
                # print(f"from sell: total_investments: {total_investments}")
                net_selling_cost = abs(y.net_total)
                net_pro_loss += (net_selling_cost - total_investments)
                total_investments = 0
                buy_sell == True
                tr += 1

                # print()
                # print(f"from sell: sum qty: {sum_qty}")
                # print(f"from sell: y.net_total: {y.net_total}")
                # print(f"from sell: total_investments: {total_investments}")
                # print(f"from sell = 0: net_pro_loss: {net_pro_loss}")
                # print()
            elif sum_qty > 0:
                # print(f"from sell = 0: net_pro_loss: {net_pro_loss}")
                net_selling_cost = abs(y.net_total)
                net_pro_loss += net_selling_cost

                total_investments -= net_pro_loss
                buy_sell == True
                tr += 1

                # print()
                # print(f"from sell = 0: sum qty: {sum_qty}")
                # print(f"from sell: y.net_total: {y.net_total}")
                # print(f"from sell: total_investments: {total_investments}")
                # print(f"from sell = 0: net_pro_loss: {net_pro_loss}")
                # print()
            # elif sum_qty == sell_qty:
            #     sum_qty -= abs(y.qty)
            #     net_selling_cost = abs(y.net_total)
            #     net_pro_loss += (total_investments - net_selling_cost)
            #     print(f"from sell = sum qty = 0: net_pro_loss: {net_pro_loss}")

            #     total_investments -= net_pro_loss
            #     print(f"from sell = sum qty = 0: net_pro_loss: {net_pro_loss}")

            #     print()
            #     print(f"from sell = sum qty: sum qty: {sum_qty}")
            #     print(f"from sell = sum qty: y.net_total: {y.net_total}")
            #     print(f"from sell = sum qty: total_investments: {total_investments}")
            #     print(f"from sell = sum qty = 0: net_pro_loss: {net_pro_loss}")
            #     print()
            #     buy_sell == True
            #     tr += 1
        if sum_qty == 0 and buy_sell == True:
            buy_sell = False
            total_investments = 0.00
        # print(f"End of for {y.script} loop---------: {itr}")
        # print()

        itr += 1

    # print(f"End of the whole loop---")
    # print()

    if net_pro_loss != 0:
        return trading_code, symb, net_pro_loss, tr
    return None, None, None, None

def get_broker_pl(**kwargs):
    # print()
    # print(f"this is get broker pl")
    # print()
    user_id = kwargs.get("user_id")
    symb = kwargs.get("script")
    trading_code = kwargs.get("trading_code")
    # net_pro_loss = kwargs.get("p_l")
    data = db.session.query(
        Transactions
    ).filter(
        Transactions.user_id == user_id,\
        Transactions.script == symb,\
        Transactions.trading_code == trading_code
    ).all()

    itr = 1
    tr = 0 # counter for number of buy-sell transactions
    broker_name = ""
    trading_code = ""
    buy_qty = 0
    sell_qty = 0
    sum_qty = 0
    total_investments = 0.00
    net_pro_loss = 0.00
    buy_sell = False

    for y in data:
        # print(f"start of for {y.trading_code} loop---------: {itr}")
        # print(f"start of for {y.script} loop---------: {itr}")
        # print(f"total investments at the start of the y loop: {total_investments}")
        # print(f"Net pro loss at the start of the y loop: {net_pro_loss}")
        broker_name = y.broker
        trading_code = y.trading_code
        # print()
        # print(f"this is from y loop: call = {y.call}")
        # print()
        if y.call == "Buy":
            buy_qty = y.qty
            sum_qty += buy_qty
            total_investments += y.net_total
            # print(f"total investments when bought {y.script} -- price {y.price} -- qty: {y.qty}: {total_investments}")

        elif y.call == "Sell":
            sell_qty = abs(y.qty)
            if sum_qty == sell_qty:
                sum_qty -= abs(y.qty)
                net_pro_loss += abs(y.net_total) - total_investments
                buy_sell == True
                total_investments = 0.00
                # print(f"net pro loos when sold {y.script} -- price {y.price} -- qty: {y.qty}: {net_pro_loss}")
                tr += 1
            elif sum_qty > sell_qty:
                sum_qty -= abs(y.qty)
                
                if total_investments < 0:
                    net_pro_loss += round((abs(y.net_total)),2)
                    total_investments = 0.00
                else:
                    net_pro_loss += round((abs(y.net_total)),2)
                    total_investments = round(total_investments - abs(y.net_total),2)
                # print(f"net pro loos when sold part {y.script} -- price {y.price} -- qty: {y.qty}: {net_pro_loss}")
                # print(f"total_investment after sold part {y.script} -- price {y.price} -- qty: {y.qty}: {total_investments}")
                # print()
                # print(f"this is if sum_qty > sell_qty")
                # print(f"total investments: {total_investments}")
                # print(f"total payment received after selling: {abs(y.net_total)}")
                # print(f"net_pro loss: {net_pro_loss}")
                # print()
                buy_sell == True
                tr += 1



        if sum_qty == 0 and buy_sell == True:
            buy_sell = False
            total_investments = 0.00
        # print()
        # print(f"this is from use database")
        # print(y.trading_code)
        # print(y.script)
        # print(y.call)
        # print(y.net_total)
        # print(f"this is net p and L: {net_pro_loss}")
        # print()

        # print(f"this is net p and L: {net_pro_loss} after loop---------: {itr}")
        # print(f"End of for {y.script} loop---------: {itr}")
        # itr += 1
    # print(f"End of the whole loop---")
    # print()
    # print(itr)
    # print(trading_code)
    # print(broker_name)
    # print(f"this is net p and L: {net_pro_loss}")
    # print()
    # if net_pro_loss != 0:
    return broker_name, trading_code, net_pro_loss, True

# -------------------End of Get Consolidated data for Holdings/Broker_Wise/Script_Wise--------------------------------------------
# -------------------Start of chk research table --------------------------------------------------------------

def chk_research_table(user_id):
    from applications.helpers import PreviousClose
    hlc_data = PreviousClose()

    user_id = user_id
    counter = 0
    open_calls = 0
    data = db.session.query(
        Research
    ).filter(
        Research.user_id == user_id,\
        Research.tgt_sl.in_(["live", "open"])
        
    ).all()
    
    for i in data:

        open_calls += 1
        high, low = hlc_data.get_high_low(i.script)

        if float(high) >= i.price and i.tgt_sl == "open":
            # print(f"{i.script}: {high} is greater than entry price: {i.price}")
            i.tgt_sl = "live"
            db.session.commit()
            counter += 1

        elif i.tgt_sl == "live":
            if float(high) >= i.target:
                i.tgt_sl = "target"
                db.session.commit()

                analyst_data = db.session.query(
                    Analysts.name
                ).filter(
                    Analysts.name == i.analyst
                ).first()
                update_analyst = GetUserData(user_id = user_id)
                update_analyst.update_sl_tgt_analyst_tabl(analyst_data.name, "target" )
                # print()
                # print(f"{i}-->{i.script}: --{i.tgt_sl}-- Market High: {high} -- target achieved --- Target: {i.target}")
                # print()
            elif float(low) <= i.stop_loss:
                i.tgt_sl = "stoploss"
                db.session.commit()

                analyst_data = db.session.query(
                    Analysts.name
                ).filter(
                    Analysts.name == i.analyst
                ).first()
                update_analyst = GetUserData(user_id = user_id)
                update_analyst.update_sl_tgt_analyst_tabl(analyst_data.name, "stoploss" )
                # print()
                # print(f"{i.script}: --{i.tgt_sl}-- low: {low} --- stop loss: {i.stop_loss} stop loss triggered")
                # print()
        else:
            pass
            # print(f"{i} -- {i.script}: --{i.tgt_sl}-- high: {high} --- {i.price}")
            # print()
    # print()
    # print(f"total number of open calls = {open_calls}")
    # print(f"total number of call entered in transactions: {counter}")
    # print()



