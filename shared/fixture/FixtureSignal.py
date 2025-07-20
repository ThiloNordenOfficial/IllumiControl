from shared.fixture.ChannelValue import ChannelValue
from shared.fixture.Fixture import Fixture


class FixtureSignal:
    def __init__(self, module: str, fixture: Fixture, channel_values: list[ChannelValue]):
        self.fixture = fixture
        self.channel_values = channel_values
        self.module = module

    def __str__(self):
        return f"FixtureSignal(module: {self.module}, fixture: {self.fixture}, channel_values: {self.channel_values})"

    def __repr__(self):
        return self.__str__()