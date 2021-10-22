from fastapi import FastAPI
from injector import Injector, Module, provider, singleton

from . import monitors, ordering


class APIModule(Module):
    @provider
    @singleton
    def app(self, container: Injector) -> FastAPI:
        app = FastAPI()
        app.state.injector = container
        app.include_router(monitors.router, prefix="/monitors")
        app.include_router(ordering.router, prefix="/orders")
        return app


__all__ = ["APIModule"]
