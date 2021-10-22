from fastapi import FastAPI
from injector import Injector
from pytest import fixture

from application.app import create_app
from application.settings import Settings


@fixture
def app() -> FastAPI:
    return create_app(Injector())


@fixture
def container(app) -> Injector:
    return app.state.injector


@fixture
def settings(container) -> Settings:
    return container.get(Settings)
