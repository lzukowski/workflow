from datetime import datetime
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, condecimal

from .types import Currency, Fiat


class BTCRate(BaseModel):
    price: condecimal(decimal_places=4)
    currency: Currency
    on_date: datetime


class CurrentPrices(BaseModel):
    updated: datetime
    prices: dict[str, condecimal(decimal_places=8)]


class ExchangeRateService:
    def __init__(self, url: str) -> None:
        self._url = urljoin(url, "bpi/currentprice.json")

    def get_bitcoin_rate(self, for_currency: Currency) -> BTCRate:
        current = self._get_prices()
        return BTCRate(
            price=current.prices[for_currency.name],
            currency=for_currency,
            on_date=current.updated,
        )

    def _get_prices(self) -> CurrentPrices:
        response = requests.get(self._url)
        response.raise_for_status()
        data = response.json()
        return CurrentPrices(
            updated=datetime.fromisoformat(data["time"]["updatedISO"]),
            prices={
                currency: Fiat(index["rate_float"])
                for currency, index in data["bpi"].items()
            }
        )
