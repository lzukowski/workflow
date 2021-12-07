from __future__ import annotations

from decimal import Decimal
from typing import Text
from uuid import UUID

from fastapi import APIRouter, Body, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, condecimal
from returns.pipeline import is_successful

from application.bus import CommandBus
from currency import Currency
from ordering import commands, errors

from .tools import Injects

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
        request: Request,
        response: Response,
        bus: CommandBus = Injects(CommandBus),
        request_id: UUID = Body(...),
        amount: condecimal(
            decimal_places=4, gt=Decimal(0), lt=Decimal(1_000_000_000),
        ) = Body(...),
        currency: Currency = Body(...),
) -> BuyOrderCreated | Response:
    result = bus.handle(
        commands.CreateBuyOrder(
            id=request_id,
            amount=amount,
            currency=Currency[currency],
        )
    )
    if is_successful(result):
        order_id = result.unwrap()
        location = request.app.url_path_for(
            "orders:get_order", order_id=str(order_id)
        )
        response.headers["Location"] = location
        response.status_code = 201
        return BuyOrderCreated(order_id=order_id, location=location)

    try:
        raise result.failure()
    except errors.OrderAlreadyExists as error:
        return RedirectResponse(
            url=request.app.url_path_for(
                "orders:get_order", order_id=str(error.order_id),
            ),
            status_code=301,
        )
    except errors.BalanceLimitExceeded as error:
        message = f"Exceeded {error.limit}BTC ordering limit"
        return JSONResponse(status_code=409, content={"detail": message})


__all__ = ["router"]
