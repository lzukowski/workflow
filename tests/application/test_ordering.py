from __future__ import annotations

import decimal
from decimal import Decimal
from typing import Optional, Text

from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import decimals
from pytest import fixture, mark


class TestOrdering:
    @mark.xfail(raises=NotImplementedError, strict=True)
    @mark.parametrize("currency", ["EUR", "GBP", "USD"])
    def test_creating_an_order(self, currency: Text, ordering):
        ordering.when_creating_buy_order_with(currency=currency)
        ordering.assert_that_order_was_created()

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_created_order_uses_current_exchange_rate(self, ordering):
        ordering.given_1btc_exchange_rate(EUR=33_681.3874)
        ordering.when_creating_buy_order_with(33_681.3874, "EUR")
        ordering.assert_that_order_was_created(with_bitcoins=1)

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_summary_amount_of_orders_cannot_exceed_100btc(self, ordering):
        ordering.given_1btc_exchange_rate(EUR=100)
        ordering.given_created_order_with(bitcoins=50)
        ordering.given_created_order_with(bitcoins=50)
        ordering.when_creating_buy_order_with(2000, "EUR")
        ordering.expect_failure_for("Exceeded 100BTC ordering limit")

    @mark.xfail(raises=NotImplementedError, strict=True)
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
            with_bitcoins=round_up(paid/exchange_rate, to_precision=8),
        )


def round_up(amount: float | Decimal, to_precision: int) -> Decimal:
    exp = Decimal(10) ** -to_precision
    return Decimal(amount).quantize(exp, rounding=decimal.ROUND_UP)


class OrderingSteps:
    def given_1btc_exchange_rate(self, **rates: Decimal | float) -> None:
        raise NotImplementedError

    def given_created_order_with(self, bitcoins: float | Decimal) -> None:
        raise NotImplementedError

    def when_creating_buy_order_with(
            self,
            amount: Optional[float | Decimal] = None,
            currency: Optional[Text] = None,
    ) -> None:
        raise NotImplementedError

    def assert_that_order_was_created(
            self, with_bitcoins: Optional[float | Decimal] = None,
    ) -> None:
        raise NotImplementedError

    def expect_failure_for(self, with_reason: Optional[Text] = None) -> None:
        raise NotImplementedError


@fixture
def ordering() -> OrderingSteps:
    return OrderingSteps()
