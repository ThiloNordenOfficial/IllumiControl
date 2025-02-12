import argparse

from audio_ingest.AudioProvider import AudioProvider
from CommandLineArgumentAdder import CommandLineArgumentAdder
from shared import LoggingConfigurator


class AudioIngest(CommandLineArgumentAdder):
    def __init__(self, args: argparse.Namespace):
        if args.list_audio_devices is not None:
            AudioProvider.list_devices()
            print("Audio devices listed, now exiting")
            exit(0)
        else:
            audio_provider = AudioProvider(args.audio_device, args.sample_rate)

    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--list-audio-devices", dest='list_audio_devices', action='store_const')
        parser.add_argument("--audio-device", dest='audio_device', required=True, type=int,
                            help="Device index of the audio input device")
        parser.add_argument("--sample-rate", dest='sample_rate', type=int)

    add_command_line_arguments = staticmethod(add_command_line_arguments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Audio Ingest',
        description='')

    AudioIngest.add_command_line_arguments(parser)
    LoggingConfigurator.add_command_line_arguments(parser)

    args = parser.parse_args()

    LoggingConfigurator(args)
    AudioIngest(args)
