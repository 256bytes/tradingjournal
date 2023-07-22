
from applications.models import Taxes, Brokers

class CalculateBrokerageAndTaxes():

    def __init__(self, code, user_id, price, qty, call ):

        self.__code = code
        self.__user_id = user_id
        self.__price = price
        self.__qty = qty
        self.__call = call

        # to get the broking charges
        # get the charges from brokers table
        self.user_broker_details = Brokers.query.filter(Brokers.trading_code == self.__code,\
                                        Brokers.user_id == self.__user_id).first()
        self.r_cnc = self.user_broker_details.equity_delivery
        self.__transaction_chgs = self.user_broker_details.transaction_chgs

        print()
        print(self.__call)
        print()
        self.__brokerage()

    def __brokerage(self):

        if self.__call != "Bonus":
            print()
            print(self.__call)
            print()
            if self.__call == "Buy": # ---------------------------------------------------------Logic for Buy

                self.r_dp_chgs = 0.00

            # r_ means this is available to the instances
            # borker type: discount broker or no discount broker
                if self.user_broker_details.broker_type == True: # ----------------------------------------(BUY) Logic for Discount Brokers

                    self.r_b = self.r_cnc
                    self.r_tb = self.r_b
                    self.r_rpu = self.__price 
                    self.r_turn_over = round(((self.__price * self.__qty) + self.r_tb), 2)
                    self.r_net_before_tax = self.r_turn_over

                    self.__taxes()

                
                else: # -----------------------------------------------------------------------------------(BUY) Logic for No Discount Brokers
                    # logic for no discount broker
                    
                    # Calculate brokerage per share and total brokerage
                    self.r_b = round(((self.r_cnc * self.__price)/100), 2)
                    self.r_tb = round((self.r_b * self.__qty), 2)
                    self.r_rpu = self.__price
                    

                    # this is for `upstox` like broker(which ever is lower condition)
                    if self.r_tb < 20 and self.user_broker_details.name == "Upstox":
                        self.r_turn_over = round((self.r_rpu * self.__qty), 2)
                        self.r_net_before_tax = round((self.r_turn_over + self.r_tb), 2)

                    elif self.r_tb >= 20 and self.user_broker_details.name == "Upstox":

                        self.r_tb = 20.00
                        self.r_turn_over = round((self.r_rpu * self.__qty), 2)
                        self.r_net_before_tax = round((self.r_turn_over + self.r_tb), 2)

                    else:
                        self.r_rpu = round((self.__price + self.r_b), 2)
                        self.r_turn_over = round((self.r_rpu * self.__qty), 2)
                        self.r_net_before_tax = self.r_turn_over

                    self.__taxes()
            
            else: # ------------------------------------------------------------------------------Logic for Sell
                self.r_dp_chgs = self.user_broker_details.dp_chgs

                if self.user_broker_details.broker_type == True: # -------------------------------(SELL) Logic for Discount Brokers 
                    self.r_b = self.r_cnc
                    self.r_tb = self.r_b
                    self.r_rpu = self.__price
                    self.r_turn_over = round(((self.__price * self.__qty) - self.r_tb), 2)
                    self.r_net_before_tax = self.r_turn_over

                    self.__taxes()

                else: # ------------------------------------------------------------------------(SELL) Logic for No Discount Brokers 
                    # Calculate brokerage per share and total brokerage
                    self.r_b = round(((self.r_cnc * self.__price)/100), 2)
                    self.r_tb = round((self.r_b * self.__qty), 2)
                    self.r_rpu = self.__price

                # this is for `upstox` like broker(which ever is lower condition)
                    if self.r_tb < 20 and self.user_broker_details.name == "Upstox":
                        self.r_turn_over = round((self.r_rpu * self.__qty), 2)
                        self.r_net_before_tax = round((self.r_turn_over - (self.r_tb + self.r_dp_chgs)), 2)

                    elif self.r_tb >= 20 and self.user_broker_details.name == "Upstox":

                        self.r_tb = 20.00
                        self.r_turn_over = round((self.r_rpu * self.__qty), 2)
                        self.r_net_before_tax = round((self.r_turn_over - (self.r_tb + self.r_dp_chgs)), 2)

                    else:
                        self.r_rpu = round((self.__price - self.r_b), 2)
                        self.r_turn_over = round((self.r_rpu * self.__qty), 2)  
                        self.r_net_before_tax = self.r_turn_over

                    self.__taxes()

        else:
            self.r_b = 0.00
            self.r_tb = 0.00
            self.r_rpu = 0.00
            self.r_net_before_tax = 0.00
            self.r_tchgs = 0.00
            self.r_dp_chgs = 0.00
            self.r_stt = 0.00
            self.r_sebi = 0.00
            self.r_sd = 0.00
            self.r_gst = 0.00
            self.r_total_taxes_without_brokerage = 0.00
            self.r_payable = 0.00


    def __taxes(self): #----------------------------------------------------------------Logic to calculate taxes.

        self.__t1 = Taxes.query.filter_by(id=1).first().stt_delivery
        self.__t2 = Taxes.query.filter_by(id=1).first().sebi_chgs
        self.__t3 = Taxes.query.filter_by(id=1).first().stamp_duty_delivery
        self.__t4 = Taxes.query.filter_by(id=1).first().gst
        self.r_tchgs = round(((self.r_turn_over * self.__transaction_chgs) / 100), 4)

        self.r_stt = round(((self.r_turn_over * self.__t1)/ 100), 4)
        self.r_sebi = round(((self.r_turn_over * self.__t2)/ 100), 4)

        # Stamp duty is applicable only for buy side
        if self.__call == "Buy":
            self.r_sd = round(((self.r_turn_over * self.__t3)/ 100), 4)
        else:
            self.r_sd = 0.0000

        self.r_gst = round((((self.r_tb + self.__transaction_chgs + self.r_sebi + self.r_dp_chgs) * self.__t4) / 100), 2)
        self.r_total_taxes_without_brokerage = round((self.r_stt + self.r_sebi + self.r_tchgs + self.r_gst), 2)

        if self.__call == "Buy":
            self.r_payable = round((self.r_net_before_tax + self.r_total_taxes_without_brokerage), 2)
        else:
            self.r_payable = round((self.r_net_before_tax - self.r_total_taxes_without_brokerage), 2)

