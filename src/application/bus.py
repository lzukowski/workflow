import logging
from datetime import datetime
from typing import Generic, Text, Type, TypeVar
from uuid import UUID, uuid4

from injector import (
    Injector,
    UnknownProvider,
    UnsatisfiedRequirement,
    inject,
    singleton,
)
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)


class Command(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_mutation = False

    def __str__(self) -> Text:
        std_str = super().__str__()
        return f"<Command:{self.__class__.__name__} {std_str}>"


class Event(BaseModel):
    command_id: UUID
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_mutation = False

    def __str__(self) -> Text:
        std_str = super().__str__()
        return f"<Event:{self.__class__.__name__} {std_str}>"


TCommand = TypeVar("TCommand")


class Handler(Generic[TCommand]):
    def __call__(self, command: TCommand) -> None:
        raise NotImplementedError


@inject
@singleton
class CommandBus:
    def __init__(self, container: Injector) -> None:
        self._get = container.get

    def handle(self, command: Command) -> None:
        log.debug(command)
        command_cls: Type[Command] = type(command)
        handler = self._get(Handler[command_cls])
        handler(command)


TEvent = TypeVar("TEvent")


class Listener(Generic[TEvent]):
    def __call__(self, event: TEvent) -> None:
        raise NotImplementedError


@inject
@singleton
class EventBus:
    def __init__(self, container: Injector) -> None:
        self._get = container.get

    def emit(self, event: TEvent) -> None:
        log.debug(event)
        event_cls: Type[TEvent] = type(event)
        try:
            listeners = self._get(list[Listener[event_cls]])
        except (UnsatisfiedRequirement, UnknownProvider):
            listeners = []

        for listener in listeners:
            listener(event)


__all__ = ["Command", "CommandBus", "Event", "EventBus", "Handler", "Listener"]
