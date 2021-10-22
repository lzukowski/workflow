import logging.config

from fastapi import FastAPI
from injector import Injector

from .api import APIModule
from .settings import Settings


def create_app(container: Injector) -> FastAPI:
    settings = container.get(Settings)
    logging.config.fileConfig(settings.config, disable_existing_loggers=False)
    container.binder.install(APIModule)
    return container.get(FastAPI)


def factory() -> FastAPI:  # pragma: no cover
    return create_app(Injector())


__all__ = ["create_app", "factory"]
