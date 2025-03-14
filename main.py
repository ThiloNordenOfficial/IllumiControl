import argparse
import logging
import signal
import threading

from CommandLineArgumentAdder import CommandLineArgumentAdder
from audio_ingest import AudioIngest
from feature_extractor import FeatureExtractor
from image_generator import ImageGenerator
from shared import LoggingConfigurator, ConfigReader
from shared.GracefulKiller import GracefulKiller


def prepare_commandline_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='IllumiControl',
        description='')
    # If a run-config file is provided, the arguments in the file will be used
    ConfigReader.add_command_line_arguments(parser)
    # If the users wants to pass their own path to the config file, the argument have to be evaluated
    config_arg = parser.parse_args()

    # To set the arguments of other modules, they have to be known first
    for argument_adder in CommandLineArgumentAdder.__subclasses__():
        argument_adder.add_command_line_arguments(parser)
    # The config file is read, if provided, and the arguments are updated
    ConfigReader(config_arg, parser)

    return parser.parse_args()


def set_shutdown_event(signum, frame):
    kill_event.set()
    logging.warning("Starting shutting down IllumiControl")


if __name__ == "__main__":

    graceful_killer = GracefulKiller()
    kill_event = graceful_killer.kill_event
    signal.signal(signal.SIGINT, set_shutdown_event)
    signal.signal(signal.SIGTERM, set_shutdown_event)

    cmdl_args = prepare_commandline_arguments()

    # Start logging
    LoggingConfigurator(cmdl_args)

    data_senders = {}
    audio_ingest = AudioIngest(cmdl_args)
    data_senders.update(audio_ingest.get_data_senders())

    image_generator = ImageGenerator(cmdl_args, data_senders)
    data_senders.update(image_generator.get_data_senders())

    feature_extractor = FeatureExtractor(cmdl_args, data_senders)

    ingest_runner = threading.Thread(target=audio_ingest.run)
    image_runner = threading.Thread(target=image_generator.run)
    feature_runner = threading.Thread(target=feature_extractor.run)

    threads = [ingest_runner, image_runner, feature_runner]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    logging.warning("Graceful shutdown of IllumiControl completed")
    # Multithreading (Audio receiver) with multiprocessing (parallelizing task of thread)
    # Optimization possible by aborting stable diffusion if taking longer than max calc time (param)
    # Compacting data structure by combining 3 values into 1
    #           e.g r 255 g 255 b 255 -> r >> shift, g >> shift, b >> shift
    #           or r 255 g 255 b 255 -> 255255255
