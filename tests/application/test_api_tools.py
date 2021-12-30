from typing import Callable

from fastapi import APIRouter, FastAPI
from fastapi.responses import PlainTextResponse
from injector import InstanceProvider, UnknownProvider
from pytest import fixture, mark, raises

from application.api.tools import Injects

Controller = Callable[[], str]


@mark.usefixtures("router")
class TestInjects:
    def test_fail_when_type_to_inject_have_no_provider(self, api_client):
        with raises(UnknownProvider):
            api_client.get("/tests/injects")

    def test_uses_injected_controller_when_bound(self, container, api_client):
        expected = "Expected response"
        container.binder.bind(Controller, to=InstanceProvider(lambda: expected))

        response = api_client.get("/tests/injects")

        assert response.status_code == 200
        assert response.text == expected

    @fixture
    def router(self, app: FastAPI) -> APIRouter:
        router = APIRouter()

        @router.get("/injects", response_class=PlainTextResponse)
        async def injects(controller=Injects(Controller)) -> str:
            return controller()

        app.include_router(router, prefix="/tests")
        return router
