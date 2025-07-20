class ChannelValue:
    def __init__(self, channel: int, value: int):
        self.channel = channel
        self.value = value

    def __str__(self):
        return F"Channel: {self.channel}, Value: {self.value}"

    def __repr__(self):
        return self.__str__()