import asyncio
import logging
import time
from asyncio import timeout

import numpy as np

from image_generator.Generator import Generator
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class RGBGenerator(Generator):
    def __init__(self, inbound_data_senders, height: int, width: int, depth: int):
        super().__init__(inbound_data_senders, height, width, depth)
        self.shape = (height, width, depth, 3)
        self.data_receiver = NumpyArrayReceiver(inbound_data_senders.get("audio-data"))
        self.timing_receiver = NumpyArrayReceiver(inbound_data_senders.get("timing-data"))

        self.rgb_data_sender = NumpyArraySender(self.shape, np.uint8)
        self.outbound_data_senders = {
            "RGB-image": self.rgb_data_sender
        }

    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        return self.outbound_data_senders

    async def _generate(self):
        logging.debug("Starting RGB-Image generator run loop")
        while True:
            try:
                timout_in_sec = float(self.timing_receiver.read_on_update()[0]) - time.time()
                async with timeout(timout_in_sec):
                    audio_data = self.data_receiver.read_on_update(timout_in_sec)
                    logging.debug("Received audio data")
                    image = np.random.randint(0, 256, self.shape, dtype=np.uint8)
                    logging.debug("Updating RGB image")
                    self.rgb_data_sender.update(image)
            except TimeoutError:
                logging.warning(F"Dropped RGB Generator step due to not finishing in time for next frame")
