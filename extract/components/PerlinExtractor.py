import logging

import numpy as np

from extract.ExtractorBase import ExtractorBase
from shared.fixture.ChannelType import ChannelType as ct
from shared.fixture.ChannelValue import ChannelValue
from shared.fixture.FixtureSignal import FixtureSignal
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


class PerlinExtractor(ExtractorBase):
    def __init__(self, data_senders):
        ExtractorBase.__init__(self, data_senders)

    def get_relevant_fixtures(self):
        return []

    async def run_procedure(self):
        rbg_data = np.ndarray((1,1,1))
        fixture_values = []
        for fixture in self.relevant_fixtures:
            channel_values = []
            rgb_values = rbg_data[fixture.position[0], fixture.position[1], fixture.position[2]]
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
            logging.debug(f"RGB Extractor setting Signal for fixture: {fixture.fixture_id}")
            self.fixture_signal_queue_sender.update(FixtureSignal(self.__class__.__name__, fixture, channel_values))
