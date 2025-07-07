import argparse
import logging
from multiprocessing import Process

from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from generator.GeneratorBase import GeneratorBase
from shared import DataSender
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.Sender import Sender


class Generators(CommandLineArgumentAdder, DataSender):
    height = None
    width = None
    depth = None

    def __init__(self, data_senders: dict[str, NumpyArraySender]):
        logging.info("Initializing image generator")
        self.generators = self._instantiate_generators(data_senders)
        self.data_senders: dict[str, NumpyArraySender] = self._get_all_data_senders()

    def _instantiate_generators(self, data_senders) -> list[GeneratorBase]:
        generators = []
        for generator_class in GeneratorBase.__subclasses__():
            generators.append(generator_class(data_senders, self.height, self.width, self.depth))
        return generators

    def _get_all_data_senders(self) -> dict[str, NumpyArraySender]:
        combined_senders = {}
        for generator in self.generators:
            combined_senders.update(generator.get_outbound_data_senders())
        return combined_senders

    def run(self):
        logging.debug("Starting generator run loop")
        generator_processes = []
        for generator in self.generators:
            generator_processes.append(Process(target=generator.run))

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

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.height = args.height
        cls.width = args.width
        cls.depth = args.depth

    def get_outbound_data_senders(self) -> dict[str, Sender]:
        return self.data_senders
