from contextlib import contextmanager
from dataclasses import dataclass
from typing import ContextManager

from injector import inject
from sqlalchemy.orm import Session, sessionmaker


@inject
@dataclass
class Transaction:
    _maker: sessionmaker

    @contextmanager
    def __call__(self) -> ContextManager[Session]:
        session = self._maker()
        try:
            yield session
            session.commit()
        except:  # noqa: E722
            session.rollback()
            raise
        finally:
            session.close()
