from uuid import UUID

from .commands import CreateBuyOrder


class Service:
    def create_buy_order(self, command: CreateBuyOrder) -> UUID:
        raise NotImplementedError
