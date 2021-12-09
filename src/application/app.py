import logging.config

from fastapi import FastAPI
from injector import Injector

from currency import CurrencyModule
from ordering import OrderingModule

from .api import APIModule
from .db import DBModule
from .settings import Settings


def create_app(container: Injector) -> FastAPI:
    settings = container.get(Settings)
    logging.config.fileConfig(settings.config, disable_existing_loggers=False)
    container.binder.install(APIModule)
    container.binder.install(DBModule)
    container.binder.install(CurrencyModule)
    container.binder.install(OrderingModule)
    return container.get(FastAPI)


def factory() -> FastAPI:  # pragma: no cover
    return create_app(Injector())


__all__ = ["create_app", "factory"]
