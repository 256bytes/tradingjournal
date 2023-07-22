from .database import db
from .models import Brokers, Funds


class ValidateUserDatabase:
    def __init__(self) -> None:
        pass

    def register_trader_code(self, trading_code):
        self.trading_code = trading_code
        if db.session.query(Brokers).filter(Brokers.trading_code == self.trading_code).first():
            return (True, f"{self.trading_code} already registered")
        else:
            return (False, None)

    def validate_trader_code(self, user_id, trading_code):
        self.user_id = user_id
        self.trading_code = trading_code

        if (
            db.session.query(Brokers.trading_code)
            .filter(Brokers.user_id == self.user_id, Brokers.trading_code == self.trading_code)
            .first()
        ):
            return (True, None)
        else:
            return (False, f"Trading Code: {self.trading_code} is Invalid or not registered.")
