from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import decimals
from pytest import fixture, mark
from sqlalchemy.orm import Session, sessionmaker

import currency
import ordering.db
from currency import BTC, Currency
from ordering.db.buy_order import DBBuyOrder
from tests.currency.factories import BTCRateFactory as BTCRate
from tests.tools import round_up, to_precision


class TestORMRepository:
    def test_properly_creates_buy_order(self, session, repository):
        request_id, rate = uuid4(), BTCRate()
        paid, bought = Decimal(100), BTC(rate.price/100)

        with repository.lock():
            order = repository.create(request_id, paid, bought, rate)
            assert order.id is not None
            assert order.request_id == request_id
            assert order.paid == paid
            assert order.bought == bought
            assert order.exchange_rate == rate

    def test_can_read_when_using_balance(self, session, repository):
        request_id, rate = uuid4(), BTCRate()
        paid, bought = Decimal(100), BTC(rate.price/100)

        with repository.lock():
            order_id = repository.create(request_id, paid, bought, rate).id

        with repository.lock():
            assert session.query(DBBuyOrder).one().id == order_id

    @given(
        paid=decimals(min_value=0.0001, max_value=100_000_000, allow_nan=False),
        rate=decimals(min_value=0.0001, max_value=100_000_000, allow_nan=False),
        bought=decimals(min_value=0.0000_0001, max_value=100, allow_nan=False),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    @mark.slow
    def test_fiat_and_btc_precision_when_saved(
            self, repository, session, paid, rate, bought,
    ):
        with repository.lock():
            btc_rate = currency.BTCRate.construct(
                price=rate, currency=Currency.EUR, on_date=datetime.utcnow()
            )
            order_id = repository.create(uuid4(), paid, bought, btc_rate).id
        session.expunge_all()

        order = session.query(DBBuyOrder).filter_by(id=order_id).one()
        assert order.paid == to_precision(paid, precision=4)
        assert order.exchange_rate.price == to_precision(rate, precision=4)
        assert order.bought == round_up(bought, precision=8)

    @fixture
    def repository(self, container) -> ordering.db.ORMRepository:
        return container.create_object(ordering.db.ORMRepository)


@fixture
def session(container) -> Session:
    session = container.get(sessionmaker)()
    yield session
    session.close()
