from __future__ import annotations

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
    def get_order_id(self, request_id: UUID) -> UUID | None:
        raise NotImplementedError
