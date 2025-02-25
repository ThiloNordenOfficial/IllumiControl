import argparse
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from CommandLineArgumentAdder import CommandLineArgumentAdder
from audio_ingest import AudioIngest
from feature_extractor import FeatureExtractor
from image_generator import ImageGenerator
from shared import LoggingConfigurator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='IllumiControl',
        description='')

    for argument_adder in CommandLineArgumentAdder.__subclasses__():
        argument_adder.add_command_line_arguments(parser)

    cmdl_args = parser.parse_args()

    LoggingConfigurator(cmdl_args)
    audio_ingest = AudioIngest(cmdl_args)
    image_generator = ImageGenerator(cmdl_args, audio_ingest.audio_data_sender)
    feature_extractor = FeatureExtractor(cmdl_args, image_generator.image_data_sender)

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
