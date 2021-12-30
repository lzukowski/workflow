from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import ContextManager, List, Text
from uuid import UUID, uuid4

import sqlalchemy as sa
import sqlalchemy_utils as sa_utils
from injector import inject
from sqlalchemy import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session

from application.bus import Event, EventBus
from application.db import Base, Transaction
from currency import BTCRate, Currency

from .interface import BuyOrder, Repository
from .types import BtcAmountColumn, FiatAmountColumn


class DBBuyOrder(Base, BuyOrder):
    def __init__(
            self,
            request_id: UUID,
            paid: Decimal,
            bought: Decimal,
            exchange_rate: BTCRate,
    ) -> None:
        self.id = uuid4()
        self.request_id = request_id
        self.paid = paid
        self.bought = bought
        self.exchange_rate = exchange_rate

    __tablename__ = "buy_orders"

    _db_id: int = sa.Column("id", sa.Integer, primary_key=True)
    id: UUID = sa.Column("order_id", sa_utils.UUIDType, unique=True)
    request_id: UUID = sa.Column(sa_utils.UUIDType, unique=True)

    paid: Decimal = sa.Column(FiatAmountColumn)
    bought: Decimal = sa.Column(BtcAmountColumn)

    _currency: Currency = sa.Column(
        "currency", sa.Enum(Currency, naive_enum=False)
    )
    _price: Decimal = sa.Column("price", FiatAmountColumn)
    _rate_date: datetime = sa.Column("rate_date", sa.DateTime)

    @hybrid_property
    def exchange_rate(self) -> BTCRate:
        return BTCRate(
            price=self._price,
            currency=self._currency,
            on_date=self._rate_date,
        )

    @exchange_rate.setter
    def exchange_rate(self, value: BTCRate) -> None:
        self._price = value.price
        self._currency = value.currency
        self._rate_date = value.on_date

    when_created: datetime = sa.Column(
        "when_created", sa.DateTime, default=datetime.utcnow, index=True
    )
    _when_updated: datetime = sa.Column(
        "when_updated", sa.DateTime, onupdate=datetime.utcnow,
    )

    def __repr__(self) -> Text:
        return (
            "<"
            f"{self.__class__.__name__}"
            f" db_id={self._db_id}"
            f" order_id={self.id}"
            f" request_id={self.request_id}"
            f" amount={self.bought!s}BTC"
            ">"
        )


@inject
class ORMRepository(Repository):
    _session: Session
    _pending_events: List[Event]

    def __init__(self, transaction: Transaction, bus: EventBus) -> None:
        self._transaction = transaction
        self._bus = bus

    @contextmanager
    def lock(self) -> ContextManager[Decimal]:
        events = []
        with self._transaction() as session:
            self._session = session
            self._pending_events = events

            lock = f"LOCK TABLE {DBBuyOrder.__tablename__} IN EXCLUSIVE MODE;"
            session.execute(lock)

            yield self._calculate_balance()

            del self._session
            del self._pending_events

        for event in events:
            self._bus.emit(event)

    def _calculate_balance(self) -> Decimal:
        balance, = self._session.query(func.sum(DBBuyOrder.bought)).one()
        return Decimal(balance or 0)

    def create(
            self,
            request_id: UUID,
            paid: Decimal,
            bought: Decimal,
            with_rate: BTCRate,
    ) -> BuyOrder:
        entry = DBBuyOrder(
            request_id=request_id,
            paid=paid,
            bought=bought,
            exchange_rate=with_rate,
        )

        self._session.add(entry)
        self._session.flush()
        return entry

    def emit(self, event: Event) -> None:
        self._pending_events.append(event)

    def get_order_id(self, for_request_id: UUID) -> BuyOrder | None:
        with self._transaction() as session:
            result = (
                session.query(DBBuyOrder.id)
                .filter_by(request_id=for_request_id)
                .one_or_none()
            )
        return result and result[0]
