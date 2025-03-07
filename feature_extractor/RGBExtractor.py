import logging
import time
from asyncio import timeout_at, timeout

from feature_extractor.Extractor import Extractor
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


class RGBExtractor(Extractor):
    def __init__(self, inbound_data_senders, fixtures):
        super().__init__(inbound_data_senders, fixtures)
        self.data_receiver = NumpyArrayReceiver(inbound_data_senders.get("RGB-image"))
        self.timing_receiver = NumpyArrayReceiver(inbound_data_senders.get("timing-data"))

    async def _extract(self):
        logging.debug("Starting RGB-Image extractor run loop")
        while True:
            try:
                timout_in_sec = float(self.timing_receiver.read_on_update()[0]) - time.time()
                async with timeout(timout_in_sec):
                    rbg_data = self.data_receiver.read_on_update(timout_in_sec)
                    dmx_frame = []
                    for fixture in self.fixtures:
                        dmx_frame.append(rbg_data[fixture.position[0], fixture.position[1], fixture.position[2]])
                    logging.debug(F"RGB Frame: {dmx_frame}")
            except TimeoutError:
                logging.warning(F"Dropped RGB Extractor step due to not finishing in time for next frame")
