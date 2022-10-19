from dataclasses import dataclass

from event_sourcery_sqlalchemy.models import configure_models
from injector import Module, provider, singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .transaction import Transaction

Base = declarative_base()


configure_models(Base)


@dataclass
class DBModule(Module):
    database_url: str

    @provider
    @singleton
    def engine(self) -> Engine:
        return create_engine(self.database_url, echo=False, future=True)

    @provider
    @singleton
    def maker(self, engine: Engine) -> sessionmaker:
        return sessionmaker(bind=engine, autoflush=False, autocommit=False)


__all__ = ["Base", "DBModule", "Transaction"]
