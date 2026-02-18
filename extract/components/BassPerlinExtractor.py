import logging

import numpy as np

from extract.ExtractorBase import ExtractorBase
from shared.fixture.ChannelType import ChannelType as ct
from shared.fixture.ChannelValue import ChannelValue
from shared.fixture.FixtureSignal import FixtureSignal
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


class BassPerlinExtractor(ExtractorBase):
    def __init__(self, data_senders):
        ExtractorBase.__init__(self, data_senders)
        self.rgb_receiver = NumpyArrayReceiver(data_senders.get("bass_rgb_image"))

    def get_relevant_fixtures(self):
        return [self.fixtures[0]]

    async def run_procedure(self):
        rbg_data = self.rgb_receiver.read_on_update()
        fixture_values = []
        for fixture in self.relevant_fixtures:
            channel_values = []
            rgb_values = rbg_data[fixture.position[0], fixture.position[1]]
            for dmx_address in fixture.dmx_addresses:
                if dmx_address[1] == ct.COLOR_RED:
                    channel_values.append(
                        ChannelValue(dmx_address[0], int(rgb_values[0])))
                elif dmx_address[1] == ct.COLOR_GREEN:
                    channel_values.append(
                        ChannelValue(dmx_address[0], int(rgb_values[1])))
                elif dmx_address[1] == ct.COLOR_BLUE:
                    channel_values.append(
                        ChannelValue(dmx_address[0], int(rgb_values[2])))
                elif dmx_address[1] == ct.CONTROL_DIMMER:
                    channel_values.append(ChannelValue(dmx_address[0], 254))

            fixture_values.append((fixture, channel_values))
            logging.debug(f"RGB Bass value setting Signal for fixture: {fixture.fixture_id}")
            self.fixture_signal_queue_sender.update(FixtureSignal(self.__class__.__name__, fixture, channel_values))
