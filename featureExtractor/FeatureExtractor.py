import argparse
import logging
import os
import pickle
from logging import getLevelName

from FixtureConfigurationLoader import FixtureConfigurationLoader


class FeatureExtractor:
    def __init__(self):
        fixtures = FixtureConfigurationLoader(args.fixture_config).fixtures
        logging.debug(fixtures)
        image = pickle.load(open(args.input, "rb"))
        for fixture in fixtures:
            logging.debug(fixture)
            logging.debug(image[fixture.position[0], fixture.position[1], :])


def prepare_logging(log_level_number):
    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARN,
        3: logging.INFO,
        4: logging.DEBUG,
    }

    log_level = log_levels[min(log_level_number, max(log_levels.keys()))]
    logging.basicConfig(level=log_level)
    logging.info(F'Loglevel: {getLevelName(log_level)}')
    logging.debug('Started')


def is_valid_file(parser_ref, arg):
    if not os.path.exists(arg):
        parser_ref.error("The file %s does not exist!" % arg)
    else:
        return arg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='FeatureExtractor',
        description='')
    parser.add_argument("-fc", "--fixture-config", dest='fixture_config', required=True,
                        type=lambda x: is_valid_file(parser, x), help="Path to the fixture configuration file")
    parser.add_argument("-i", "--input", dest='input', required=True, type=lambda x: is_valid_file(parser, x),
                        help="Path to the input file used as source for color extraction")
    parser.add_argument("-v", "--verbose", dest="verbosity", action="count", default=0,
                        help="Verbosity (between 1-4 occurrences with more leading to more "
                             "verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, "
                             "DEBUG=4")
    args = parser.parse_args()
    prepare_logging(args.verbosity)
    FeatureExtractor()
