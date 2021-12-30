from unittest.mock import Mock, call
from uuid import uuid4

from injector import InstanceProvider, UnknownProvider
from pytest import fixture, raises

from application.bus import (
    Command,
    CommandBus,
    Event,
    EventBus,
    Handler,
    Listener,
)


class TestCommandBus:
    def test_unknown_provider_when_command_has_no_handler(self, bus, command):
        with raises(UnknownProvider):
            bus.handle(command)

    def test_failure_when_handler_raises_error(self, bus, command, handler):
        handler.side_effect = Exception
        with raises(Exception):
            bus.handle(command)
        handler.assert_called_once_with(command)

    def test_successful_when_command_processed(self, bus, command, handler):
        bus.handle(command)
        handler.assert_called_once_with(command)

    @fixture
    def command(self) -> Command:
        return Command()

    @fixture
    def handler(self, container):
        _handler = Mock()
        container.binder.bind(Handler[Command], to=InstanceProvider(_handler))
        return _handler

    @fixture
    def bus(self, container):
        return container.get(CommandBus)


class TestEventBus:
    def test_nothing_when_no_listener_for_event(self, bus, event):
        bus.emit(event)

    def test_listener_receives_event_when_emitted(self, container, bus, event):
        listener = Mock(Listener[Event])
        container.binder.multibind(list[Listener[Event]], to=[listener])

        bus.emit(event)
        assert listener.call_args == call(event)

    def test_call_all_listeners_when_event_emitted(self, container, bus, event):
        listeners = [Mock(Listener[Event]) for _ in range(5)]
        container.binder.multibind(list[Listener[Event]], to=listeners)

        bus.emit(event)
        assert all(listener.call_args == call(event) for listener in listeners)

    @fixture
    def event(self) -> Event:
        return Event(command_id=uuid4())

    @fixture
    def bus(self, container) -> EventBus:
        return container.get(EventBus)
