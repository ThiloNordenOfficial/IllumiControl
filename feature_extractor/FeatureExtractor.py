import argparse
import logging
import pickle
import time

from CommandLineArgumentAdder import CommandLineArgumentAdder
from feature_extractor.FixtureConfigurationLoader import FixtureConfigurationLoader
from shared import is_valid_file, LoggingConfigurator
from shared.shared_memory import NumpyArraySender
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


class FeatureExtractor(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace, image_data_sender: NumpyArraySender):
        self.fixtures = FixtureConfigurationLoader(args.fixture_config).fixtures
        self.image_data_receiver = NumpyArrayReceiver(image_data_sender)
        logging.debug("Initializing feature extractor")

    def run(self):
        logging.debug("Starting feature extractor run loop")
        while True:
            image = self.image_data_receiver.read_on_update()
            logging.debug("Received image data")
            # TODO think about more complex extraction methods than just reading the pixel values
            # multiprocessing to parallelize the extraction of features might be feasible
            for fixture in self.fixtures:
                self.extract_dmx_values(fixture, image)

    def extract_dmx_values(self, fixture, image):
        rgb_value = image[fixture.position[0], fixture.position[1], fixture.position[2]]
        logging.debug(f"Fixture {fixture.type} at position {fixture.position} has RGB value {rgb_value}")

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("-fc", "--fixture-config", dest='fixture_config', required=True,
                            type=lambda x: is_valid_file(parser, x), help="Path to the fixture configuration file")
        # TODO For dev purposes, till the image is generated
        parser.add_argument("-i", "--input", dest='input', required=True, type=lambda x: is_valid_file(parser, x),
                            help="Path to the debug image")

    add_command_line_arguments = staticmethod(add_command_line_arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Feature Extractor',
        description='')

    FeatureExtractor.add_command_line_arguments(parser)
    LoggingConfigurator.add_command_line_arguments(parser)

    args = parser.parse_args()

    LoggingConfigurator(args)
    FeatureExtractor(args)
