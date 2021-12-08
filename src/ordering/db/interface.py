from abc import abstractmethod
from decimal import Decimal
from typing import ContextManager, Optional
from uuid import UUID

from application.bus import Event
from currency import BTCRate


class BuyOrder:
    id: UUID
    request_id: UUID
    paid: Decimal
    bought: Decimal
    exchange_rate: BTCRate


class Repository:
    @abstractmethod
    def lock(self) -> ContextManager[Decimal]:
        """
        Locks balance of BuyOrders.
        :return: Context manager with current balance
        """
        raise NotImplementedError

    @abstractmethod
    def create(
            self,
            request_id: UUID,
            paid: Decimal,
            bought: Decimal,
            with_rate: BTCRate,
    ) -> BuyOrder:
        """
        Usage: Needs locked context before creating BuyOrder.
        """
        raise NotImplementedError

    @abstractmethod
    def emit(self, event: Event) -> None:
        """
        Usage: Needs locked context before creating BuyOrder.
        """
        raise NotImplementedError

    @abstractmethod
    def get_order_id(self, for_request_id: UUID) -> Optional[UUID]:
        raise NotImplementedError
