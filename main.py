import argparse
import logging
import threading
from CommandLineArgumentAdder import CommandLineArgumentAdder
from audio_ingest import AudioIngest
from feature_extractor import FeatureExtractor
from image_generator import ImageGenerator
from shared import LoggingConfigurator, ConfigReader

if __name__ == "__main__":
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

    cmdl_args = parser.parse_args()
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

    # FeatureExtractor(cmdl_args)
    # parallelization
    #### Multithreading (Audio receiver) with multiprocessing (parralalizing task of thread)
    # Optimization possible by aborting stable diffusion if taking longer than max calc time (param)
    # Compacting data structure by combining 3 values into 1
    #           e.g r 255 g 255 b 255 -> r >> shift, g >> shift, b >> shift
    #           or r 255 g 255 b 255 -> 255255255
