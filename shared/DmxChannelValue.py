class DmxChannelValue:
    def __init__(self, fixture_id: int, channel: int, value: int):
        self.fixture_id = fixture_id
        self.channel = channel
        self.value = value

    def __str__(self):
        return F"Fixture: {self.fixture_id}, Channel: {self.channel}, Value: {self.value}"

    def __repr__(self):
        return self.__str__()