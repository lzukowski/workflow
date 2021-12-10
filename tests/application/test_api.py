from random import random
from uuid import uuid4

from pytest import mark

from .factories import ApiCreateBuyOrderRequestFactory as CreateBuyOrder

CREATE_ORDER_URL = "/orders/"


class TestCreateBuyOrderRequest:
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
