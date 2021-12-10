from uuid import uuid4

from pytest import fixture
from sqlalchemy.orm import sessionmaker

from ordering.queries import BuyOrder, BuyOrdersQueries

from .factories import DBBuyOrderFactory as DBBuyOrder


class TestGetOrderId:
    def test_none_when_no_buy_order_for_request(self, queries):
        assert queries.get_order_id(uuid4()) is None

    def test_order_id_when_buy_order_found(self, queries, request_id, order_id):
        assert queries.get_order_id(request_id) == order_id

    @fixture
    def request_id(self):
        return uuid4()

    @fixture
    def order_id(self, session, request_id):
        order = DBBuyOrder(request_id=request_id)
        order_id = order.id
        session.add(order)
        session.commit()
        session.expunge_all()
        return order_id


class TestGetOrder:
    def test_none_when_no_buy_order_found(self, queries):
        assert queries.get_order(uuid4()) is None

    def test_order_when_buy_order_found(self, queries, buy_order):
        assert queries.get_order(buy_order.id) == buy_order

    @fixture
    def buy_order(self, session):
        entry = DBBuyOrder()
        session.add(entry)
        session.commit()

        buy_order = BuyOrder(
            id=entry.id,
            request_id=entry.request_id,
            bitcoins=entry.bought,
            bought_for=entry.paid,
            currency=entry.exchange_rate.currency,
        )

        session.expunge_all()
        return buy_order


@fixture
def queries(container):
    return container.get(BuyOrdersQueries)


@fixture
def session(container):
    session = container.get(sessionmaker)()
    yield session
    session.close()
