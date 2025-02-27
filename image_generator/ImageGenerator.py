import argparse
import logging
import numpy as np

from CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import LoggingConfigurator
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class ImageGenerator(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace, audio_data_sender: NumpyArraySender):
        logging.debug("Initializing image generator")
        self.height = args.height
        self.width = args.width
        self.depth = args.depth
        self.audio_data_receiver = NumpyArrayReceiver(audio_data_sender)
        self.image_data_sender = NumpyArraySender((self.height, self.width, self.depth, 3), dtype=np.uint8)

    def run(self):
        logging.debug("Starting image generator run loop")
        while True:
            audio_data = self.audio_data_receiver.read_on_update()
            logging.debug("Received audio data")
            # TODO ACTUAL IMAGE GENERATIO
            image = np.random.randint(0, 256, (self.height, self.width, self.depth, 3), dtype=np.uint8)
            self.image_data_sender.update(image)
            logging.debug("Updated image data")

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--width", dest='width', type=int, default=10, help="Width of the image in pixels")
        parser.add_argument("--height", dest='height', type=int, default=10,
                            help="Height of the image in pixels")
        parser.add_argument("--depth", dest='depth', type=int, default=10, help="Depth of the image in pixels")

    add_command_line_arguments = staticmethod(add_command_line_arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Image Generator',
        description='')
    # Only add those arguments if run stand-alone
    parser.add_argument("--audio-memory-name", dest='audio_memory_name', required=True)
    parser.add_argument("--audio-memory-shape", dest='audio_memory_shape')
    parser.add_argument("--audio-memory-dtype", dest='audio_memory_dtype')

    ImageGenerator.add_command_line_arguments(parser)
    LoggingConfigurator.add_command_line_arguments(parser)

    args = parser.parse_args()

    LoggingConfigurator(args)
    ig = ImageGenerator(args, args.audio_memory_name, (1, 6373), np.float64)
    ig.run()
