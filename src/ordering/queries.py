from __future__ import annotations

from uuid import UUID

from injector import inject
from pydantic import BaseModel, condecimal
from sqlalchemy.orm import sessionmaker

from currency import Currency

from .db.buy_order import DBBuyOrder


class BuyOrder(BaseModel):
    id: UUID
    request_id: UUID
    bitcoins: condecimal(decimal_places=8)
    bought_for: condecimal(decimal_places=4)
    currency: Currency

    @classmethod
    def from_db(cls, entry: DBBuyOrder) -> BuyOrder:
        return cls(
            id=entry.id,
            request_id=entry.request_id,
            bitcoins=entry.bought,
            bought_for=entry.paid,
            currency=entry.exchange_rate.currency,
        )


@inject
class BuyOrdersQueries:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    def get_order_id(self, request_id: UUID) -> UUID | None:
        query = (
            self._session_maker()
            .query(DBBuyOrder.id)
            .filter_by(request_id=request_id)
        )
        return (result := query.one_or_none()) and result[0]

    def get_order(self, order_id: UUID) -> BuyOrder | None:
        session = self._session_maker()
        query = session.query(DBBuyOrder).filter_by(id=order_id)
        entry = query.one_or_none()
        session.expunge_all()
        session.rollback()
        return entry and BuyOrder.from_db(entry)


__all__ = ["BuyOrder", "BuyOrdersQueries"]
