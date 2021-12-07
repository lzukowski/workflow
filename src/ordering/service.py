from .commands import CreateBuyOrder


class Service:
    def create_buy_order(self, command: CreateBuyOrder) -> None:
        raise NotImplementedError
