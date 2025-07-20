import logging

from extract.ExtractorBase import ExtractorBase
from shared.fixture.ChannelType import ChannelType as ct
from shared.fixture.ChannelValue import ChannelValue
from shared.fixture.FixtureSignal import FixtureSignal
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


class RGBExtractor(ExtractorBase):
    def __init__(self, data_senders, fixtures, fixtures_signal_queue):
        super().__init__(data_senders, fixtures, fixtures_signal_queue)
        self.rgb_data_receiver = NumpyArrayReceiver(data_senders.get("RGB-image"))
        self.relevant_fixtures = [fixture for fixture in fixtures if fixture.dmx_addresses[1] == ct.COLOR_RED or
                                  ct.COLOR_GREEN or
                                  ct.COLOR_BLUE]

    async def run_procedure(self):
        rbg_data = self.rgb_data_receiver.read_on_update()
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
            fixture_values.append((fixture, channel_values))
            logging.debug(f"RGB Extractor setting Signal for fixture: {fixture.fixture_id}")
            self.fixture_signal_queue_sender.update(FixtureSignal(self.__class__.__name__, fixture, channel_values))
