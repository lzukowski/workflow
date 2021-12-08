from dataclasses import dataclass
from decimal import Decimal
from typing import cast

from injector import Injector, Module, provider

from application.bus import Handler

from . import commands, errors, events, queries
from .commands import CreateBuyOrder
from .service import Service


@dataclass
class OrderingModule(Module):
    ordered_btc_limit: Decimal

    @provider
    def service(self, container: Injector) -> Service:
        return container.create_object(
            Service,
            additional_kwargs={"ordered_btc_limit": self.ordered_btc_limit},
        )

    @provider
    def create_buy_order(self, ordering: Service) -> Handler[CreateBuyOrder]:
        return cast(Handler[CreateBuyOrder], ordering.create_buy_order)


__all__ = [
    "commands",
    "errors",
    "events",
    "Service",
    "OrderingModule",
    "queries",
]
