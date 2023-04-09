
from applications.models import Brokers

class RemoveBrokerage():

    def __init__(self, code, user_id, price, qty):
        self.__code = code
        self.__user_id = user_id
        self.__price = price
        self.__qty = qty

        self.__brokerage()

    def __brokerage(self):

        # to get the broking charges
        brokers_chgs = Brokers.query.filter(Brokers.trading_code == self.__code, Brokers.user_id == self.__user_id).first()
 

        # borker type: discount broker or no discount broker
        # r_ means this is available to the instances


        if brokers_chgs.type == True:
            self.r_cnc = brokers_chgs.equity_delivery
            self.r_intra = brokers_chgs.equity_intraday

            self.r_b = self.r_cnc
            self.r_tb = self.r_b

            self.r_rpu = ((self.__price*100) / (100+self.r_b))

        else:
            # logic for no discount broker
            self.r_cnc = brokers_chgs.equity_delivery
            self.r_intra = brokers_chgs.equity_intraday

            self.r_b = ((self.r_cnc * self.__price)/100)

            self.r_tb = (self.r_b * self.__qty)

            if self.r_tb < 20:
                pass
            else:
                self.r_tb = 20
            
            self.r_rpu = ((self.__price*100) / (100+self.r_b))

                

   