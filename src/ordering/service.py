import logging
from decimal import Decimal

from injector import inject

from currency import BTC, ExchangeRateService

from .commands import CreateBuyOrder
from .db import Repository
from .errors import BalanceLimitExceeded, OrderAlreadyExists
from .events import BuyOrderCreated

log = logging.getLogger(__name__)


@inject
class Service:
    def __init__(
            self,
            ordered_btc_limit: Decimal,
            repository: Repository,
            exchange_rates: ExchangeRateService,
    ) -> None:
        self._bought_btc_limit = ordered_btc_limit
        self._repository = repository
        self._get_btc_rate = exchange_rates.get_bitcoin_rate

    def create_buy_order(self, command: CreateBuyOrder) -> None:
        log.info(command)

        if (order_id := self._repository.get_order_id(command.id)) is not None:
            raise OrderAlreadyExists(order_id)

        rate = self._get_btc_rate(command.currency)
        btc = BTC(command.amount / rate.price)

        with self._repository.lock() as current_balance:
            if current_balance + btc > self._bought_btc_limit:
                raise BalanceLimitExceeded(self._bought_btc_limit)

            order = self._repository.create(
                command.id, command.amount, btc, rate,
            )
            created = BuyOrderCreated(
                command_id=command.id,
                order_id=order.id,
                bitcoins=btc,
            )
            log.info(created)
            self._repository.emit(created)
