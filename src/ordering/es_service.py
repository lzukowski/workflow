from injector import inject

from .commands import CreateBuyOrder
from .service import Service


@inject
class ESService(Service):
    def create_buy_order(self, command: CreateBuyOrder) -> None:
        raise NotImplementedError
