import argparse

import numpy as np

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
        self.data_receiver = NumpyArrayReceiver(data_senders.get("audio-data"))
        self.rgb_data_sender = NumpyArraySender(self.shape, np.uint8)
        self.outbound_data_senders = {
            "RGB-image": self.rgb_data_sender
        }

    def delete(self):
        self.data_receiver.close()
        self.timing_receiver.close()
        for sender in self.outbound_data_senders.values():
            sender.close()

    async def run_procedure(self):
        audio_data = self.data_receiver.read_on_update()
        image = np.random.randint(0, 256, self.shape, dtype=np.uint8)
        self.rgb_data_sender.update(image)

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
