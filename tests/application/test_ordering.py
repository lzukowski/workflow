from __future__ import annotations

from decimal import Decimal
from typing import Optional, Text
from uuid import uuid4

from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import decimals
from pytest import fixture, mark
from requests import Response

from tests.application.factories import (
    ApiCreateBuyOrderRequestFactory as CreateBuyOrder,
)
from tests.tools import CoinDeskApiStub, round_up


class TestOrdering:
    @mark.parametrize("currency", ["EUR", "GBP", "USD"])
    def test_creating_an_order(self, currency: Text, ordering):
        ordering.when_creating_buy_order_with(currency=currency)
        ordering.assert_that_order_was_created()

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_created_order_uses_current_exchange_rate(self, ordering):
        ordering.given_1btc_exchange_rate(EUR=33_681.3874)
        ordering.when_creating_buy_order_with(33_681.3874, "EUR")
        ordering.assert_that_order_was_created(with_bitcoins=1)

    def test_summary_amount_of_orders_cannot_exceed_100btc(self, ordering):
        ordering.given_1btc_exchange_rate(EUR=100)
        ordering.given_created_order_with(bitcoins=50)
        ordering.given_created_order_with(bitcoins=50)
        ordering.when_creating_buy_order_with(2000, "EUR")
        ordering.expect_failure_for("Exceeded 100BTC ordering limit")

    @mark.xfail(raises=NotImplementedError, strict=True)
    @mark.slow
    @given(
        paid=decimals(min_value=0.0001, max_value=999.9999, places=4),
        exchange_rate=decimals(min_value=20_000, max_value=90_000, places=4),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_bought_bitcoins_are_round_up_with_precision_of_8_digits(
            self, paid: Decimal, exchange_rate: Decimal, ordering,
    ):
        ordering.given_1btc_exchange_rate(EUR=exchange_rate)
        ordering.when_creating_buy_order_with(paid, "EUR")
        ordering.assert_that_order_was_created(
            with_bitcoins=round_up(paid/exchange_rate, precision=8),
        )


class OrderingSteps:
    def __init__(
            self, api_client: TestClient, coindesk: CoinDeskApiStub,
    ) -> None:
        self.client = api_client
        self.coindesk = coindesk
        self.last_response: Response | None = None

    @property
    def create_order_url(self) -> Text:
        return self.client.app.url_path_for("orders:create_order")

    def given_1btc_exchange_rate(self, **rates: Decimal | float) -> None:
        for currency, index in rates.items():
            self.coindesk.set_current(Decimal(index), currency)

    def given_created_order_with(self, bitcoins: float | Decimal) -> None:
        index = self.coindesk.get_bitcoin_rate("EUR")
        response = self.client.post(
            url=self.create_order_url,
            json=CreateBuyOrder(amount=float(bitcoins * index), currency="EUR"),
        )
        assert response.status_code == 201

    def when_creating_buy_order_with(
            self,
            amount: Optional[float | Decimal] = None,
            currency: Optional[Text] = None,
    ) -> None:
        command_args = {}
        if amount:
            command_args["amount"] = float(amount)
        if currency:
            command_args["currency"] = currency

        body = CreateBuyOrder(request_id=str(uuid4()), **command_args)
        self.last_response = self.client.post(self.create_order_url, json=body)

    def assert_that_order_was_created(
            self, with_bitcoins: Optional[float | Decimal] = None,
    ) -> None:
        assert self.last_response.status_code == 201
        if with_bitcoins:
            order_location = self.last_response.headers["Location"]
            order = self.client.get(order_location).json()
            assert order["bitcoins"] == float(with_bitcoins)

    def expect_failure_for(self, with_reason: Optional[Text] = None) -> None:
        assert self.last_response.status_code != 201
        if with_reason is not None:
            assert self.last_response.json()["detail"] == with_reason


@fixture
def ordering(
        api_client: TestClient, coindesk: CoinDeskApiStub,
) -> OrderingSteps:
    return OrderingSteps(api_client, coindesk)
