import argparse
import configparser

from shared.validators import is_valid_file


class ConfigReader:
    def __init__(self, args: argparse.Namespace, parser: argparse.ArgumentParser):
        print("Initializing config reader")

        if args.config is None:
            print("No config file provided")
            return

        self.config = configparser.ConfigParser()
        self.config.read(args.config)
        self.update_arguments(parser)

    def update_arguments(self, parser: argparse.ArgumentParser):
        arguments = {k: v for section in self.config.sections() for k, v in self.config.items(section)}

        for action in parser._actions:
            if action.dest in arguments:
                action.required = False
                action.default = arguments[action.dest]

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--config", type=lambda x: is_valid_file(parser, x),
                            help="Path to the config file to extract the arguments from. If provided,"
                                 "the arguments in the file will be used and the command line arguments will be ignored."
                                 "If not provided, the command line arguments will be used.")

    add_command_line_arguments = staticmethod(add_command_line_arguments)
