
class DmxConverter:
    def __init__(self):
        self.dmx = pydmx.DMXConnection('/dev/ttyUSB0')

    def set_channel(self, channel, value):
        self.dmx.setChannel(channel, value)

    def set_channels(self, channels):
        for channel, value in channels.items():
            self.set_channel(channel, value)

    def close(self):
        self.dmx.close()