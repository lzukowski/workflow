from unittest.mock import Mock

from injector import InstanceProvider, UnknownProvider
from pytest import fixture, raises

from application.bus import Command, CommandBus, Handler


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
