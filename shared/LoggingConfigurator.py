import argparse
import logging

import coloredlogs

from CommandLineArgumentAdder import CommandLineArgumentAdder


class LoggingConfigurator(CommandLineArgumentAdder):
    verbosity = None

    def __init__(self):
        log_levels = {
            0: logging.CRITICAL,
            1: logging.ERROR,
            2: logging.WARN,
            3: logging.INFO,
            4: logging.DEBUG,
        }
        log_level = log_levels[min(int(self.verbosity), max(log_levels.keys()))]
        coloredlogs.install(level=log_level,
                            fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s {%(filename)s:%(lineno)d} %(message)s")
        logging.info(F'Starting with log level: {logging.getLevelName(log_level)}')

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                            help="Verbosity (between 0-4 occurrences with more leading to more "
                                 "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                                 "DEBUG=4")

    add_command_line_arguments = staticmethod(add_command_line_arguments)

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.verbosity = args.verbosity