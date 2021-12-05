from injector import InstanceProvider, UnknownProvider
from pytest import fixture, mark, raises

from application.bus import Command, CommandBus, Handler


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
