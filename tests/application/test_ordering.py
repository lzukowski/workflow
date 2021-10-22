from __future__ import annotations

import decimal
from decimal import Decimal
from typing import Optional, Text
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from hypothesis import given
from hypothesis.strategies import decimals, uuids
from pytest import fixture, mark

from tests.application.factories import (
    ApiCreateBuyOrderRequestFactory as CreateBuyOrder,
)
from tests.tools import CoinDeskApiMock


class TestOrdering:
    @fixture(autouse=True)
    def setup(self, api_client: TestClient, coindesk: CoinDeskApiMock):
        self.client = api_client
        self.coindesk = coindesk
        self._responses = {}

    @fixture
    def req_id(self):
        return uuid4()

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_creating_an_order(self, req_id: UUID):
        self.given_1btc_exchange_rate(33_681.3874, "GBP")
        self.when_creating_buy_order_with(req_id, 10, "GBP")
        self.assert_that_order_was_created_for(req_id)

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_created_order_uses_current_exchange_rate(self, req_id):
        self.given_1btc_exchange_rate(33_681.3874, "GBP")
        self.when_creating_buy_order_with(req_id, 33_681.3874, "GBP")
        self.assert_that_order_was_created_for(req_id, with_bitcoins=1)

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_summary_amount_of_orders_cannot_exceed_100btc(self, req_id):
        self.given_1btc_exchange_rate(100, "GBP")
        self.given_created_order_with(bitcoins=50)
        self.given_created_order_with(bitcoins=50)
        self.when_creating_buy_order_with(req_id, 2000, "GBP")
        self.expect_failure_for(
            req_id, with_reason="Exceeded 100BTC ordering limit",
        )

    @mark.xfail(raises=NotImplementedError, strict=True)
    @given(
        req_id=uuids(),
        paid=decimals(min_value=0.0000001, max_value=99.99999999, places=4),
        exchange_rate=decimals(min_value=20_000, max_value=90_000, places=4),
    )
    def test_bought_bitcoins_are_round_up_with_precision_of_8_digits(
            self, req_id: UUID, paid: Decimal, exchange_rate: Decimal,
    ):
        self.given_1btc_exchange_rate(exchange_rate, "GBP")
        self.when_creating_buy_order_with(req_id, paid, "GBP")
        self.assert_that_order_was_created_for(
            req_id, with_bitcoins=round_up(paid/exchange_rate, to_precision=8),
        )

    def given_1btc_exchange_rate(
            self, index: Decimal | float, currency: Text,
    ) -> None:
        self.coindesk.set_current(Decimal(index), currency)

    def given_created_order_with(self, bitcoins: float | Decimal) -> UUID:
        request_id = uuid4()
        index = self.coindesk.get_bitcoin_rate("GBP")
        self.when_creating_buy_order_with(
            request_id, amount=float(Decimal(bitcoins) * index), currency="GBP",
        )
        self.assert_that_order_was_created_for(request_id)
        return request_id

    def when_creating_buy_order_with(
            self,
            request_id: UUID,
            amount: Optional[float | Decimal] = None,
            currency: Optional[Text] = None,
    ) -> None:
        command_args = {}
        if amount:
            command_args["amount"] = float(amount)
        if currency:
            command_args["currency"] = currency

        url = self.client.app.url_path_for("orders:create_order")
        body = CreateBuyOrder(request_id=str(request_id), **command_args)
        self._responses[request_id] = self.client.post(url, json=body)

    def assert_that_order_was_created_for(
            self,
            request_id: UUID,
            with_bitcoins: Optional[float | Decimal] = None,
    ) -> None:
        response = self._responses[request_id]
        assert response.status_code == 201

        if with_bitcoins:
            order_location = response.headers["Location"]
            order = self.client.get(order_location).json()
            assert order["bitcoins"] == float(with_bitcoins)

    def expect_failure_for(
            self, request_id: UUID, with_reason: Optional[Text] = None,
    ) -> None:
        response = self._responses[request_id]
        assert response.status_code != 201

        if with_reason is not None:
            assert response.json()["detail"] == with_reason


def round_up(amount: float | Decimal, to_precision: int) -> Decimal:
    exp = Decimal("1." + to_precision * "0")
    return Decimal(amount).quantize(exp, rounding=decimal.ROUND_UP)
