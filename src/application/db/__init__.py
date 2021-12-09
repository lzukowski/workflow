from injector import Module, provider, singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

from application.settings import Settings

Base = declarative_base()


class DBModule(Module):
    @provider
    @singleton
    def engine(self, settings: Settings) -> Engine:
        return create_engine(settings.database_url, echo=False, future=True)


__all__ = ["Base", "DBModule"]
