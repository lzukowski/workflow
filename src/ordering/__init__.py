from typing import cast

from injector import Injector, Module, provider

from application.bus import Handler

from . import commands, db, errors, events, queries
from .commands import CreateBuyOrder
from .service import Service


class OrderingModule(Module):
    @provider
    def create_buy_order(self, ordering: Service) -> Handler[CreateBuyOrder]:
        return cast(Handler[CreateBuyOrder], ordering.create_buy_order)

    @provider
    def orm_repository(self, container: Injector) -> db.Repository:
        return container.create_object(db.ORMRepository)


__all__ = [
    "commands",
    "errors",
    "events",
    "Service",
    "OrderingModule",
    "queries",
]
