from typing import cast

from injector import Module, provider

from application.bus import Handler

from . import commands, errors, events
from .commands import CreateBuyOrder
from .service import Service


class OrderingModule(Module):
    @provider
    def create_buy_order(self, ordering: Service) -> Handler[CreateBuyOrder]:
        return cast(Handler[CreateBuyOrder], ordering.create_buy_order)


__all__ = ["commands", "errors", "events", "Service", "OrderingModule"]
