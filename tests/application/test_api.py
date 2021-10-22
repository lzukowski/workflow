from functools import partial
from random import random
from uuid import uuid4

from pytest import fixture, mark

from .factories import ApiCreateBuyOrderRequestFactory as CreateBuyOrder


class TestCreateBuyOrderRequest:
    @fixture
    def post(self, api_client):
        url = api_client.app.url_path_for("orders:create_order")
        return partial(api_client.post, url)

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_after_creating_redirects_to_created_order(self, post, api_client):
        request = CreateBuyOrder()
        response = post(json=request)
        assert response.status_code == 201
        order_url = response.headers["Location"]
        order = api_client.get(order_url).json()
        assert order["request_id"] == request["request_id"]

    @mark.xfail(raises=NotImplementedError, strict=True)
    def test_creating_order_is_idempotent(self, post):
        request = CreateBuyOrder()
        order_url = post(json=request).headers["Location"]
        assert order_url == post(json=request).headers["Location"]

    @mark.parametrize(
        "request_id", ["ILLEGAL", uuid4().hex[:-3], "", random(), None]
    )
    def test_reject_when_no_uuid_id(self, post, request_id):
        request = CreateBuyOrder().update(request_id=request_id)
        response = post(json=request)
        assert response.status_code == 422

    def test_reject_when_negative_amount(self, post):
        request = CreateBuyOrder().update(amount=-1)
        response = post(json=request)
        assert response.status_code == 422

    def test_reject_when_amount_higher_than_1_000_000_000(self, post):
        request = CreateBuyOrder().update(amount=1_000_000_000)
        response = post(json=request)
        assert response.status_code == 422

    @mark.parametrize("currency", ["PLN", "AUD", "XXX"])
    def test_reject_when_currency_not_eur_gbp_usd(self, post, currency):
        request = CreateBuyOrder().update(currency=currency)
        response = post(json=request)
        assert response.status_code == 422
