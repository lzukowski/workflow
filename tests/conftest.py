import alembic.command
import alembic.config
from fastapi import FastAPI
from injector import Injector
from pytest import fixture, mark
from sqlalchemy.engine import Engine

from application.app import create_app
from application.settings import Settings
from tests.tools import CoinDeskApiStub


def pytest_addoption(parser):
    parser.addoption("--skip-slow", action="store_true", default=False)


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--skip-slow"):
        return
    skip_slow = mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@fixture
def app() -> FastAPI:
    return create_app(Injector())


@fixture
def container(app) -> Injector:
    return app.state.injector


@fixture
def settings(container) -> Settings:
    return container.get(Settings)


@fixture
def coindesk(settings: Settings) -> CoinDeskApiStub:
    coindesk_mock = CoinDeskApiStub(settings.coindesk_api_url)
    with coindesk_mock() as coindesk:
        yield coindesk


@fixture(autouse=True)
def db_migrate(container):
    config = container.get(Settings).config
    engine = container.get(Engine)
    with engine.begin():
        alembic.command.upgrade(alembic.config.Config(config), "head")
    yield
    with engine.begin():
        alembic.command.downgrade(alembic.config.Config(config), "base")
