from fastapi import FastAPI
from injector import Injector, Module, provider, singleton

from . import monitors


class APIModule(Module):
    @provider
    @singleton
    def app(self, container: Injector) -> FastAPI:
        app = FastAPI()
        app.state.injector = container
        app.include_router(monitors.router, prefix="/monitors")
        return app


__all__ = ["APIModule"]
