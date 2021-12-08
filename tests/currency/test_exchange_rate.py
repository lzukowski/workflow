from unittest.mock import ANY

from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import decimals, integers
from pytest import fixture, mark, raises
from requests import HTTPError

from currency import BTCRate, Currency, ExchangeRateService


class TestExchangeRateService:
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(rate=decimals(min_value=0.0001, max_value=999.9999, places=4))
    @mark.parametrize("currency", list(Currency))
    def test_actual_currency_rates_when_requesting_rates(
            self, currency, rate, coindesk, service,
    ):
        coindesk.set_current(rate, currency)
        assert service.get_bitcoin_rate(currency) == BTCRate.construct(
            price=rate, currency=currency, on_date=ANY,
        )

    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(status_code=integers(min_value=400, max_value=599))
    def test_raises_when_http_error(self, status_code, coindesk, service):
        with coindesk.temporal_issue(status_code), raises(HTTPError):
            service.get_bitcoin_rate(Currency.EUR)

    @fixture
    def service(self, container):
        return container.get(ExchangeRateService)
