import logging
from decimal import Decimal
from functools import singledispatchmethod

from event_sourcery import Aggregate, Repository
from event_sourcery.interfaces.event import Event
from injector import inject

from currency import ExchangeRateService, BTC
from .commands import CreateBuyOrder
from .service import Service

log = logging.getLogger(__name__)


class BuyOrder(Aggregate):
    def __init__(self) -> None:
        super().__init__()
        self._amount: Decimal | None = None

    class Placed(Event):
        btc_amount: Decimal

    class AlreadyPlaced(ValueError):
        pass

    def place(self, btc: Decimal) -> None:
        if self._amount is not None:
            raise BuyOrder.AlreadyPlaced()
        self._event(BuyOrder.Placed, btc_amount=btc)

    @singledispatchmethod
    def _apply(self, event: Event) -> None:
        raise NotImplementedError

    @_apply.register
    def _apply_placement(self, event: Placed) -> None:
        self._amount = event.btc_amount


@inject
class ESService(Service):
    def __init__(
            self,
            repository: Repository[BuyOrder],
            exchange_rates: ExchangeRateService,
    ) -> None:
        self._repository = repository
        self._get_btc_rate = exchange_rates.get_bitcoin_rate

    def create_buy_order(self, command: CreateBuyOrder) -> None:
        log.info(command)
        rate = self._get_btc_rate(command.currency)
        btc = BTC(command.amount / rate.price)
        with self._repository.aggregate(command.id) as buy_order:
            buy_order.place(btc)

        raise NotImplementedError
