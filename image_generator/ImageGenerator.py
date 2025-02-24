import argparse
import logging
import time
import numpy as np

from CommandLineArgumentAdder import CommandLineArgumentAdder
from image_generator import AudioDataReceiver
from shared import LoggingConfigurator


class ImageGenerator(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace, name, shape, dtype):
        logging.debug("Initializing image generator")
        self.adr = AudioDataReceiver(name, shape, dtype)

    def run(self):
        logging.debug("Starting image generator run loop")
        while True:
            data = self.adr.read_array()
            # TODO REMOVE
            time.sleep(0.05)
            print(F"received data {data}")

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        pass

    add_command_line_arguments = staticmethod(add_command_line_arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Image Generator',
        description='')
    ## Only add those arguments if run stand-alone
    parser.add_argument("--audio-memory-name", dest='audio_memory_name', required=True)
    parser.add_argument("--audio-memory-shape", dest='audio_memory_shape')
    parser.add_argument("--audio-memory-dtype", dest='audio_memory_dtype')

    ImageGenerator.add_command_line_arguments(parser)
    LoggingConfigurator.add_command_line_arguments(parser)

    args = parser.parse_args()

    LoggingConfigurator(args)
    ig = ImageGenerator(args, args.audio_memory_name, (1, 6373), np.float64)
    ig.run()
