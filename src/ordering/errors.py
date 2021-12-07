from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class BalanceLimitExceeded(Exception):
    limit: Decimal


@dataclass(frozen=True)
class OrderAlreadyExists(Exception):
    order_id: UUID
