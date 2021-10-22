from decimal import Decimal
from typing import Text
from uuid import UUID

from fastapi import APIRouter, Body
from pydantic import BaseModel, condecimal

from currency import Currency

router = APIRouter()


class BuyOrder(BaseModel):
    id: UUID
    request_id: UUID
    bitcoins: condecimal(decimal_places=8)
    bought_for: condecimal(decimal_places=4)
    currency: Currency


@router.get(
    "/{order_id}", name="orders:get_order", response_model=BuyOrder,
)
async def get_order(order_id: UUID) -> BuyOrder:
    raise NotImplementedError


class CreateBuyOrderError(BaseModel):
    detail: Text


class BuyOrderCreated(BaseModel):
    order_id: UUID
    location: Text


@router.post(
    "/", name="orders:create_order",
    status_code=201,
    response_model=BuyOrderCreated,
    responses={409: {"model": CreateBuyOrderError}},
)
async def create_order(
        request_id: UUID = Body(...),
        amount: condecimal(
            decimal_places=4, gt=Decimal(0), lt=Decimal(1_000_000_000),
        ) = Body(...),
        currency: Currency = Body(...),
) -> BuyOrderCreated:
    raise NotImplementedError

__all__ = ["router"]
