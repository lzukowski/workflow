from decimal import Decimal
from random import random
from unittest.mock import ANY, Mock
from uuid import UUID, uuid4

from fastapi import FastAPI
from injector import InstanceProvider
from mockito import when
from pytest import fixture, mark

from currency import Currency
from ordering import Service as OrderingService
from ordering import commands, errors

from .factories import ApiCreateBuyOrderRequestFactory as CreateBuyOrder

CREATE_ORDER_URL = "/orders/"


class TestCreateBuyOrderRequest:
    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_after_creating_redirects_to_created_order(self, api_client):
        request = CreateBuyOrder()
        response = api_client.post(CREATE_ORDER_URL, json=request)
        assert response.status_code == 201
        order_url = response.headers["Location"]
        order = api_client.get(order_url).json()
        assert order["request_id"] == request["request_id"]

    def test_creating_order_is_idempotent(self, api_client):
        request = CreateBuyOrder()
        first = api_client.post(CREATE_ORDER_URL, json=request)
        second = api_client.post(CREATE_ORDER_URL, json=request)
        assert first.headers["Location"] == second.headers["Location"]

    @mark.parametrize(
        "request_id", ["ILLEGAL", uuid4().hex[:-3], "", random(), None]
    )
    def test_reject_when_no_uuid_id(self, api_client, request_id):
        request = CreateBuyOrder().update(request_id=request_id)
        response = api_client.post(CREATE_ORDER_URL, json=request)
        assert response.status_code == 422

    def test_reject_when_negative_amount(self, api_client):
        request = CreateBuyOrder().update(amount=-1)
        response = api_client.post(CREATE_ORDER_URL, json=request)
        assert response.status_code == 422

    def test_reject_when_amount_higher_than_1_000_000_000(self, api_client):
        request = CreateBuyOrder().update(amount=1_000_000_000)
        response = api_client.post(CREATE_ORDER_URL, json=request)
        assert response.status_code == 422

    @mark.parametrize("currency", ["PLN", "AUD", "XXX"])
    def test_reject_when_currency_not_eur_gbp_usd(self, api_client, currency):
        request = CreateBuyOrder().update(currency=currency)
        response = api_client.post(CREATE_ORDER_URL, json=request)
        assert response.status_code == 422


class TestCreateBuyOrderController:
    def test_201_when_created(
            self, app, api_client, create_buy_order, order_url,
    ):
        response = api_client.post(CREATE_ORDER_URL, json=create_buy_order)
        assert response.status_code == 201
        assert response.headers["Location"] == order_url

    def test_301_when_already_created(
            self, api_client, ordering, order_id, order_url,
    ):
        when(ordering).create_buy_order(ANY).thenRaise(
            errors.OrderAlreadyExists(order_id)
        )

        response = api_client.post(CREATE_ORDER_URL, json=CreateBuyOrder())

        assert response.status_code == 301
        assert response.headers["Location"] == order_url

    def test_409_when_order_limit_exceeded(self, api_client, ordering):
        when(ordering).create_buy_order(ANY).thenRaise(
            errors.BalanceLimitExceeded(Decimal(100))
        )

        response = api_client.post(CREATE_ORDER_URL, json=CreateBuyOrder())

        assert response.status_code == 409
        assert response.json()["detail"] == "Exceeded 100BTC ordering limit"

    @fixture
    def create_buy_order(self) -> dict:
        return CreateBuyOrder()

    @fixture
    def order_id(self) -> UUID:
        return uuid4()

    @fixture
    def order_url(self, app: FastAPI, order_id: UUID) -> str:
        return app.url_path_for("orders:get_order", order_id=str(order_id))

    @fixture(autouse=True)
    def ordering(
            self, container, create_buy_order, order_id,
    ) -> OrderingService:
        service = Mock(spec=OrderingService)
        when(service).create_buy_order(
            commands.CreateBuyOrder.construct(
                id=UUID(hex=create_buy_order["request_id"]),
                amount=(
                    Decimal(create_buy_order["amount"])
                    .quantize(Decimal(10) ** -4)
                ),
                currency=Currency[create_buy_order["currency"]],
                timestamp=ANY,
            )
        ).thenReturn(order_id)

        container.binder.bind(OrderingService, to=InstanceProvider(service))
        return service
