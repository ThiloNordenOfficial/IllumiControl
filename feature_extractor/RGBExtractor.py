import logging
import time
from asyncio import timeout

from ipcqueue.posixmq import Queue

from feature_extractor.Extractor import Extractor
from feature_extractor.fixture import ChannelType as ct
from shared.DmxChannelValue import DmxChannelValue
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


class RGBExtractor(Extractor):
    def __init__(self, inbound_data_senders, fixtures):
        super().__init__(inbound_data_senders, fixtures)
        logging.error(fixtures)
        self.dmx_queue = Queue("/dmx_queue")
        self.data_receiver = NumpyArrayReceiver(inbound_data_senders.get("RGB-image"))
        self.timing_receiver = NumpyArrayReceiver(inbound_data_senders.get("timing-data"))
        self.relevant_fixtures = [fixture for fixture in fixtures if fixture.dmx_addresses[1] == ct.COLOR_RED or
                                  ct.COLOR_GREEN or
                                  ct.COLOR_BLUE]

    async def _extract(self):
        logging.debug("Starting RGB-Image extractor run loop")
        while True:
            try:
                timout_in_sec = float(self.timing_receiver.read_on_update()[0]) - time.time()
                async with timeout(timout_in_sec):
                    rbg_data = self.data_receiver.read_on_update(timout_in_sec)
                    dmx_frame = []
                    for fixture in self.relevant_fixtures:
                        rgb_values = rbg_data[fixture.position[0], fixture.position[1], fixture.position[2]]
                        for dmx_address in fixture.dmx_addresses:
                            if dmx_address[1] == ct.COLOR_RED:
                                dmx_frame.append(
                                    DmxChannelValue(fixture.fixture_id, dmx_address[0], int(rgb_values[0])))
                            elif dmx_address[1] == ct.COLOR_GREEN:
                                dmx_frame.append(
                                    DmxChannelValue(fixture.fixture_id, dmx_address[0], int(rgb_values[1])))
                            elif dmx_address[1] == ct.COLOR_BLUE:
                                dmx_frame.append(
                                    DmxChannelValue(fixture.fixture_id, dmx_address[0], int(rgb_values[2])))
                    self.dmx_queue.put(dmx_frame)
            except TimeoutError:
                logging.warning(F"Dropped RGB Extractor step due to not finishing in time for next frame")
