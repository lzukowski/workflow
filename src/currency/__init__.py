from dataclasses import dataclass

from injector import Module, provider

from .exchange_rate import BTCRate, ExchangeRateService
from .types import BTC, Currency, Fiat


@dataclass
class CurrencyModule(Module):
    coindesk_url: str

    @provider
    def service(self) -> ExchangeRateService:
        return ExchangeRateService(self.coindesk_url)


__all__ = [
    "BTC",
    "BTCRate",
    "Currency",
    "CurrencyModule",
    "ExchangeRateService",
    "Fiat",
]
