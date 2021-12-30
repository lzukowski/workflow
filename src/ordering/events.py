from uuid import UUID

from pydantic import condecimal

from application.bus import Event


class BuyOrderCreated(Event):
    order_id: UUID
    bitcoins: condecimal(decimal_places=8)
