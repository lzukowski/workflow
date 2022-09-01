from dataclasses import dataclass
from decimal import Decimal
from typing import cast

from injector import Module, provider, Binder, ClassProvider, InstanceProvider

from application.bus import Handler

from . import commands, db, errors, events, queries
from .commands import CreateBuyOrder
from .service import Service, OrderedBTCLimit


@dataclass
class OrderingModule(Module):
    ordered_btc_limit: Decimal

    def configure(self, binder: Binder) -> None:
        binder.bind(OrderedBTCLimit, to=InstanceProvider(self.ordered_btc_limit))
        binder.bind(db.Repository, to=ClassProvider(db.ORMRepository))

    @provider
    def create_buy_order(self, ordering: Service) -> Handler[CreateBuyOrder]:
        return cast(Handler[CreateBuyOrder], ordering.create_buy_order)


__all__ = [
    "commands",
    "errors",
    "events",
    "Service",
    "OrderedBTCLimit",
    "OrderingModule",
    "queries",
]
