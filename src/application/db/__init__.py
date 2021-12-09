from dataclasses import dataclass

from injector import Module, provider, singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


@dataclass
class DBModule(Module):
    database_url: str

    @provider
    @singleton
    def engine(self) -> Engine:
        return create_engine(self.database_url, echo=False, future=True)


__all__ = ["Base", "DBModule"]
