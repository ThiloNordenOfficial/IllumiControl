from shared.fixture.ChannelValue import ChannelValue


class DmxSignal:
    def __init__(self, universe: int, channel_values: list[ChannelValue]):
        self.universe = universe
        self.channel_values = channel_values

    def __str__(self):
        return f"DmxSignal(universe: {self.universe}, channel_values: {self.channel_values})"

    def __repr__(self):
        return self.__str__()