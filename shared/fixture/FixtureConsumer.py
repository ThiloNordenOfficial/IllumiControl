import argparse

from shared.fixture.FixtureConfigurationLoader import FixtureConfigurationLoader
from shared.CommandLineArgumentAdder import CommandLineArgumentAdder
from shared.validators.is_valid_file import is_valid_file


class FixtureConsumer(CommandLineArgumentAdder):
    fixture_config = None

    def __init__(self):
        self.fixtures = FixtureConfigurationLoader(self.fixture_config).fixtures


    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("-fc", "--fixture-config", dest='fixture_config', required=True,
                            type=lambda x: is_valid_file(parser, x), help="Path to the fixture configuration file")
    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.fixture_config = args.fixture_config

