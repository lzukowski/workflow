from datetime import datetime

from pydantic import BaseModel, condecimal

from .types import Currency


class BTCRate(BaseModel):
    price: condecimal(decimal_places=4)
    currency: Currency
    on_date: datetime


class ExchangeRateService:
    def get_bitcoin_rate(self, for_currency: Currency) -> BTCRate:
        raise NotImplementedError
