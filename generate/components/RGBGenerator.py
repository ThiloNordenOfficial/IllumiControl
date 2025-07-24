import argparse
import logging

import numpy as np
from torchaudio.functional import loudness

from generate import GeneratorBase
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.SmSender import SmSender


class RGBGenerator(GeneratorBase, CommandLineArgumentAdder):
    height = None
    width = None
    depth = None

    def __init__(self, data_senders):
        GeneratorBase.__init__(self,data_senders)
        CommandLineArgumentAdder.__init__(self)

        self.shape = (self.height, self.width, self.depth, 3)
        self.loudness_receiver = NumpyArrayReceiver(data_senders.get("loudness-data"))
        self.rgb_data_sender = NumpyArraySender(self.shape, np.uint8)
        self.outbound_data_senders = {
            "RGB-image": self.rgb_data_sender
        }

    def delete(self):
        self.loudness_receiver.close()
        self.timing_receiver.close()
        for sender in self.outbound_data_senders.values():
            sender.close()

    async def run_procedure(self):
        loudness_min = 0
        loudness_max = 100
        loudness = self.loudness_receiver.read_on_update()[0][0]
        t = np.clip((loudness - loudness_min) / (loudness_max - loudness_min), 0.0, 1.0)
        low = int(t * 255)
        self.rgb_data_sender.update(np.random.randint(low, 256, size=self.shape, dtype=np.uint8))

    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        return self.outbound_data_senders

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--width", dest='width', type=int, default=10, help="Width of the image in pixels")
        parser.add_argument("--height", dest='height', type=int, default=10,
                            help="Height of the image in pixels")
        parser.add_argument("--depth", dest='depth', type=int, default=10, help="Depth of the image in pixels")

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.height = args.height
        cls.width = args.width
        cls.depth = args.depth
