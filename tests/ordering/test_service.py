from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import timedelta
from decimal import Decimal
from typing import ContextManager, Type
from unittest.mock import ANY, Mock
from uuid import UUID, uuid4

from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import decimals
from injector import Injector
from mockito import when
from pytest import approx, fixture, mark, raises

import ordering.db
from application.bus import Event
from application.settings import Settings
from currency import Currency, ExchangeRateService
from ordering import Service
from ordering.db import BuyOrder
from ordering.errors import BalanceLimitExceeded, OrderAlreadyExists
from ordering.events import BuyOrderCreated
from tests.currency.factories import BTCRateFactory as BTCRate
from tests.tools import round_up

from .factories import CreateBuyOrderFactory as CreateBuyOrder


class TestOrderingService:
    def test_raises_when_order_already_created(self, ordering):
        command = CreateBuyOrder()
        ordering.create_buy_order(command)

        with raises(OrderAlreadyExists):
            ordering.create_buy_order(command)

    def test_raises_when_exceeding_order_limit(self, ordering):
        ordering.set_limit_on_ordered_btc(0.0000_0001)

        with raises(BalanceLimitExceeded) as exceeded:
            ordering.create_buy_order(amount=99_999)

        assert float(exceeded.value.limit) == approx(0.0000_0001)

    def test_emmit_event_when_buy_order_created(self, ordering):
        cmd_id = uuid4()
        ordering.create_buy_order(command_id=cmd_id)
        ordering.expect(BuyOrderCreated, command_id=cmd_id)

    @settings(
        max_examples=1000,
        deadline=timedelta(seconds=20),
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        paid=decimals(min_value=0.0001, max_value=999_999.9999, places=4),
        exchange_rate=decimals(min_value=20_000, max_value=90_000, places=4),
    )
    @mark.slow
    def test_btc_are_round_up_to_8_decimal_digits_when_buying(
            self, paid: Decimal, exchange_rate: Decimal, ordering,
    ):
        ordering.set_exchange_rate(to=exchange_rate)
        order_id = ordering.create_buy_order(amount=paid)

        expected = round_up(paid/exchange_rate, precision=8)
        ordering.expect(BuyOrderCreated, bitcoins=expected, order_id=order_id)


class InMemoryRepository(ordering.db.Repository):
    emitted: list[Event]

    def __init__(self):
        self._orders_by_req_id: dict[UUID, BuyOrder] = {}

    @contextmanager
    def lock(self) -> ContextManager[Decimal]:
        self.emitted = []
        yield sum(order.bought for order in self._orders_by_req_id.values())

    def create(
            self,
            request_id: UUID,
            paid: Decimal,
            bought: Decimal,
            with_rate: BTCRate,
    ) -> BuyOrder:
        self._orders_by_req_id[request_id] = Mock(
            BuyOrder,
            id=uuid4(),
            request_id=request_id,
            paid=paid,
            bought=bought,
            exchange_rate=with_rate,
        )
        return self._orders_by_req_id[request_id]

    def emit(self, event: Event) -> None:
        self.emitted.append(event)

    def get_order_id(self, for_request_id: UUID) -> UUID:
        order = self._orders_by_req_id.get(for_request_id)
        return order and order.id


class OrderingSteps:
    def __init__(self, container: Injector) -> None:
        self._repository = InMemoryRepository()
        self._btc_limit = container.get(Settings).ordered_btc_limit
        self._container = container
        self._exchange_rates = Mock(ExchangeRateService)
        self.set_exchange_rate(33_234)

    @property
    def _service(self) -> Service:
        return self._container.create_object(
            Service,
            additional_kwargs={
                "repository": self._repository,
                "exchange_rates": self._exchange_rates,
                "ordered_btc_limit": self._btc_limit,
            }
        )

    def set_limit_on_ordered_btc(self, to: Decimal | float) -> None:
        self._btc_limit = Decimal(to).quantize(Decimal(10)**-8)

    def create_buy_order(
            self,
            command: ordering.CreateBuyOrder | None = None,
            **attributes,
    ) -> None:
        if "command_id" in attributes:
            attributes["id"] = attributes.pop("command_id")
        self._service.create_buy_order(
            command or CreateBuyOrder(**attributes)
        )

    def set_exchange_rate(self, to: Decimal | float | int) -> None:
        price = Decimal(to).quantize(Decimal(10) ** -4)
        for c in Currency:
            rate = BTCRate(currency=c, price=price)
            when(self._exchange_rates).get_bitcoin_rate(c).thenReturn(rate)

    def expect(self, event_type: Type[Event], **event_attributes) -> None:
        fields = {
            field: event_attributes.get(field) or ANY
            for field in event_type.schema()["properties"].keys()
        }
        assert event_type.construct(**fields) in self._repository.emitted


@fixture
def ordering(container) -> OrderingSteps:
    os.environ["ORDERED_BTC_LIMIT"] = "999_999_999"
    return OrderingSteps(container)
