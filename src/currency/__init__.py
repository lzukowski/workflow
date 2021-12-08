from injector import Module, provider

from application.settings import Settings

from .exchange_rate import BTCRate, ExchangeRateService
from .types import BTC, Currency, Fiat


class CurrencyModule(Module):
    @provider
    def service(self, settings: Settings) -> ExchangeRateService:
        return ExchangeRateService(settings.coindesk_api_url)


__all__ = [
    "BTC",
    "BTCRate",
    "Currency",
    "CurrencyModule",
    "ExchangeRateService",
    "Fiat",
]
