from injector import Module, provider, singleton
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker

from application.settings import Settings

from .transaction import Transaction

Base = declarative_base()


class DBModule(Module):
    @provider
    @singleton
    def engine(self, settings: Settings) -> Engine:
        return create_engine(settings.database_url, echo=False, future=True)

    @provider
    @singleton
    def maker(self, engine: Engine) -> sessionmaker:
        return sessionmaker(bind=engine, autoflush=False, autocommit=False)


__all__ = ["Base", "DBModule", "Transaction"]
