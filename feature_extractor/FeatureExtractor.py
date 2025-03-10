import argparse
import logging
from multiprocessing import Process

from CommandLineArgumentAdder import CommandLineArgumentAdder
from feature_extractor.Extractor import Extractor
from feature_extractor.fixture import FixtureConfigurationLoader
from shared import is_valid_file
from shared.shared_memory import NumpyArraySender
from shared.validators.is_valid_ip import is_valid_ip


class FeatureExtractor(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace, data_senders: dict[str, NumpyArraySender]):
        self.fixtures = FixtureConfigurationLoader(args.fixture_config).fixtures
        self.dmx_sender = {}
        self.extractors = self._instantiate_extractors(data_senders)
        logging.debug("Initializing feature extractor")

    def _instantiate_extractors(self, data_senders) -> list[Extractor]:
        extractors = []
        for extractor_class in Extractor.__subclasses__():
            extractors.append(extractor_class(data_senders, self.fixtures))
        return extractors

    def run(self):
        logging.debug("Starting feature extractor run loop")
        extractor_processes = []
        for extractor in self.extractors:
            extractor_processes.append(Process(target=extractor.extract))

        for process in extractor_processes:
            process.start()

        for process in extractor_processes:
            process.join()

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("-fc", "--fixture-config", dest='fixture_config', required=True,
                            type=lambda x: is_valid_file(parser, x), help="Path to the fixture configuration file")
        # TODO For dev purposes, till the image is generated
        parser.add_argument("-i", "--input", dest='input_image', required=True, type=lambda x: is_valid_file(parser, x),
                            help="Path to the debug image")
        parser.add_argument("--artnet-ip", dest='artnet_ip', required=True, type=lambda x: is_valid_ip(parser, x),
                            help="IP of the artnet server")

    add_command_line_arguments = staticmethod(add_command_line_arguments)
