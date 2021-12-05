import logging
from datetime import datetime
from typing import Any, Callable, Generic, Text, Type, TypeVar
from uuid import UUID, uuid4

from injector import Injector, inject, singleton
from pydantic import BaseModel, Field
from returns.result import Result, safe

log = logging.getLogger(__name__)


class Command(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def __str__(self) -> Text:
        std_str = super().__str__()
        return f"<Command:{self.__class__.__name__} {std_str}>"


TCommand = TypeVar("TCommand")


class Handler(Generic[TCommand]):
    def __call__(self, command: TCommand) -> Any:
        raise NotImplementedError


Callback = Callable[[Result], None]


@inject
@singleton
class CommandBus:
    def __init__(self, container: Injector) -> None:
        self._get = container.get

    def handle(self, command: Command) -> Result:
        log.debug(command)
        command_cls: Type[Command] = type(command)
        handler = safe(self._get(Handler[command_cls]))
        result = handler(command)
        log.debug(result)
        return result


__all__ = ["Command", "CommandBus", "Handler"]
