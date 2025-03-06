import logging

from feature_extractor.Extractor import Extractor
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


class RGBExtractor(Extractor):
    def __init__(self, inbound_data_senders, fixtures):
        super().__init__(inbound_data_senders, fixtures)
        self.data_receiver = NumpyArrayReceiver(inbound_data_senders.get("RGB-image"))

    def extract(self):
        logging.debug("Starting RGB-Image extractor run loop")
        while True:
            rbg_data = self.data_receiver.read_on_update()
            dmx_frame = []
            for fixture in self.fixtures:
                dmx_frame.append(rbg_data[fixture.position[0], fixture.position[1], fixture.position[2]])
            logging.debug(F"RGB Frame: {dmx_frame}")
