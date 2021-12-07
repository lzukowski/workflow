from unittest.mock import Mock, call
from uuid import uuid4

from injector import InstanceProvider, UnknownProvider
from pytest import fixture, mark, raises

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

    @mark.usefixtures("failing_handler")
    def test_failure_when_handler_raises_error(self, bus, command):
        result = bus.handle(command)
        assert isinstance(result.failure(), Exception)
        assert command == result.failure().args[0]

    @mark.usefixtures("returns_command_id_handler")
    def test_result_when_calling_command(self, bus, command):
        result = bus.handle(command)
        assert result.unwrap() == command.id

    @fixture
    def command(self) -> Command:
        return Command()

    @fixture
    def failing_handler(self, container):
        def _handler(command: Command) -> None:
            raise Exception(command)

        container.binder.bind(Handler[Command], to=InstanceProvider(_handler))

    @fixture
    def returns_command_id_handler(self, container):
        container.binder.bind(
            Handler[Command], to=InstanceProvider(lambda c: c.id)
        )

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
