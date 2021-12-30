from abc import abstractmethod
from decimal import Decimal
from typing import ContextManager, Optional, Protocol
from uuid import UUID

from application.bus import Event
from currency import BTCRate


class BuyOrder:
    id: UUID
    request_id: UUID
    paid: Decimal
    bought: Decimal
    exchange_rate: BTCRate


class Repository(Protocol):
    @abstractmethod
    def lock(self) -> ContextManager[Decimal]:
        """
        Locks balance of BuyOrders.
        :return: Context manager with current balance
        """
        ...

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
        ...

    @abstractmethod
    def emit(self, event: Event) -> None:
        """
        Usage: Needs locked context before creating BuyOrder.
        """
        ...

    @abstractmethod
    def get_order_id(self, for_request_id: UUID) -> Optional[UUID]:
        ...
