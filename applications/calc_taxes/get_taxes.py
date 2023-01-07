
from applications.models import Taxes, Brokers

class CaluculateBrokerageAndTaxes():

    def __init__(self, code, user_id, price, qty, call ):

        self.__code = code
        self.__user_id = user_id
        self.__price = price
        self.__qty = qty
        self.__call = call

        self.__brokerage()

    def __brokerage(self):

        # to get the broking charges
        brokers_chgs = Brokers.query.filter(Brokers.trading_code == self.__code, Brokers.user_id == self.__user_id).first()

        # borker type: discount broker or no discount broker
        # r_ means this is available to the instances
        if brokers_chgs.type == True:
            self.r_cnc = brokers_chgs.equity_delivery
            self.r_intra = brokers_chgs.equity_intraday
            self.__transaction_chgs = brokers_chgs.transaction_chgs

            if self.__call == "buy":
                self.r_dp_chgs = 0
            else:
                self.r_dp_chgs = brokers_chgs.dp_chgs

            self.r_b = self.r_cnc
            self.r_tb = self.r_b
            self.r_rpu = self.__price
            self.r_turn_over = (self.r_rpu * self.__qty)
            self.r_net_before_tax = ((self.r_rpu ) * (self.__qty))

            self.__taxes()

        else:
            # logic for no discount broker
            self.r_cnc = brokers_chgs.equity_delivery
            self.r_intra = brokers_chgs.equity_intraday
            self.__transaction_chgs = brokers_chgs.transaction_chgs
            self.r_dp_chgs = brokers_chgs.dp_chgs

            self.r_b = ((self.r_cnc * self.__price)/100)
            self.r_tb = (self.r_b * self.__qty)

    
            if self.r_tb < 20:
                pass
            else:
                self.r_tb = 20
            
            self.r_rpu = (self.__price + self.r_b)
            self.r_turn_over = (self.r_rpu * self.__qty)
            self.r_net_before_tax = ((self.r_rpu + self.r_b) * (self.__qty))

            self.__taxes()

    def __taxes(self):

        self.__t1 = Taxes.query.filter_by(id=1).first().stt_delivery
        self.__t2 = Taxes.query.filter_by(id=1).first().sebi_chgs
        self.__t3 = Taxes.query.filter_by(id=1).first().stamp_duty_delivery
        self.__t4 = Taxes.query.filter_by(id=1).first().gst

        self.r_tchgs = ((self.r_turn_over * self.__transaction_chgs) / 100)
        self.r_stt = ((self.r_turn_over * self.__t1)/ 100)
        self.r_sebi = ((self.r_turn_over * self.__t2)/ 100)

        # Stamp duty is applicable only for buy side
        if self.__call == "buy":
            self.r_sd = ((self.r_turn_over * self.__t3)/ 100)
        else:
            self.r_sd = 0

        self.r_gst = (((self.r_tb + self.__transaction_chgs + self.r_sebi) * self.__t4) / 100)
        self.r_total_taxes_others = (self.r_tb + self.r_stt + self.r_sebi + self.r_tchgs + self.r_gst + self.r_dp_chgs)

    
        if self.__call == "buy":
            self.r_payable = (self.r_turn_over + self.r_total_taxes_others)
        else:
            self.r_payable = (self.r_turn_over - self.r_total_taxes_others)

