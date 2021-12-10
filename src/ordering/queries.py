from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, condecimal

from currency import Currency


class BuyOrder(BaseModel):
    id: UUID
    request_id: UUID
    bitcoins: condecimal(decimal_places=8)
    bought_for: condecimal(decimal_places=4)
    currency: Currency


class BuyOrdersQueries:
    def get_order(self, order_id: UUID) -> Optional[BuyOrder]:
        raise NotImplementedError
