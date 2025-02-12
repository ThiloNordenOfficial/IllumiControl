import argparse
import logging
import pickle

from CommandLineArgumentAdder import CommandLineArgumentAdder
from feature_extractor.FixtureConfigurationLoader import FixtureConfigurationLoader
from shared import is_valid_file, LoggingConfigurator


class FeatureExtractor(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace):
        fixtures = FixtureConfigurationLoader(args.fixture_config).fixtures
        image = pickle.load(open(args.input, "rb"))
        for fixture in fixtures:
            logging.debug(fixture)
            logging.debug(image[fixture.position[0], fixture.position[1], :])

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
