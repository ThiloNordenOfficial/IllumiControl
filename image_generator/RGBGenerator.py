import logging

import numpy as np

from image_generator.Generator import Generator
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class RGBGenerator(Generator):
    def __init__(self, inbound_data_senders, height: int, width: int, depth: int):
        super().__init__(inbound_data_senders, height, width, depth)
        self.shape = (height, width, depth, 3)
        self.data_receiver = NumpyArrayReceiver(inbound_data_senders.get("audio-data"))
        self.rgb_data_sender = NumpyArraySender(self.shape, np.uint8)
        self.outbound_data_senders = {
            "RGB-image": self.rgb_data_sender
        }

    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        return self.outbound_data_senders

    def generate(self):
        logging.debug("Starting RGB-Image generator run loop")
        while True:
            audio_data = self.data_receiver.read_on_update()
            logging.debug("Received audio data")
            image = np.random.randint(0, 256, self.shape, dtype=np.uint8)
            self.rgb_data_sender.update(image)
            logging.debug("Updated RGB image")
