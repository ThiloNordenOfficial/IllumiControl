import argparse
import logging
from multiprocessing import Process

from CommandLineArgumentAdder import CommandLineArgumentAdder
from image_generator.Generator import Generator
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class ImageGenerator(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace, data_senders: dict[str, NumpyArraySender]):
        logging.debug("Initializing image generator")
        self.height = args.height
        self.width = args.width
        self.depth = args.depth
        self.generators = self._instantiate_generators(data_senders)
        self.data_senders: dict[str, NumpyArraySender] = self._get_all_data_senders()

    def _instantiate_generators(self, data_senders) -> list[Generator]:
        generators = []
        for generator_class in Generator.__subclasses__():
            generators.append(generator_class(data_senders, self.height, self.width, self.depth))
        return generators

    def _get_all_data_senders(self) -> dict[str, NumpyArraySender]:
        combined_senders = {}
        for generator in self.generators:
            combined_senders.update(generator.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting image generator run loop")
        generator_processes = []
        for generator in self.generators:
            generator_processes.append(Process(target=generator.generate))

        for process in generator_processes:
            process.start()

        for process in generator_processes:
            process.join()

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--width", dest='width', type=int, default=10, help="Width of the image in pixels")
        parser.add_argument("--height", dest='height', type=int, default=10,
                            help="Height of the image in pixels")
        parser.add_argument("--depth", dest='depth', type=int, default=10, help="Depth of the image in pixels")

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    def get_data_senders(self) -> dict[str, NumpyArraySender]:
        return self.data_senders
