from uuid import uuid4

from pytest import fixture
from sqlalchemy.orm import sessionmaker

from ordering.queries import BuyOrdersQueries

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


@fixture
def queries(container):
    return container.get(BuyOrdersQueries)


@fixture
def session(container):
    session = container.get(sessionmaker)()
    yield session
    session.close()
