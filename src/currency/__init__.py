from dataclasses import dataclass
from typing import Text

from injector import Module, Binder, InstanceProvider

from .exchange_rate import BTCRate, CoindeskUrl, ExchangeRateService
from .types import BTC, Currency, Fiat


@dataclass
class CurrencyModule(Module):
    coindesk_url: Text

    def configure(self, binder: Binder) -> None:
        binder.bind(CoindeskUrl, to=InstanceProvider(self.coindesk_url))


__all__ = [
    "BTC",
    "BTCRate",
    "CoindeskUrl",
    "Currency",
    "CurrencyModule",
    "ExchangeRateService",
    "Fiat",
]
