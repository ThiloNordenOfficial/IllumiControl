import argparse
import logging
from typing import Set

from stupidArtnet import StupidArtnet

from sender.SenderBase import SenderBase
from shared.fixture import Fixture
from shared.fixture.DmxSignal import DmxSignal
from shared.shared_memory import SmSender
from shared.validators.is_valid_ip import is_valid_ip


class ArtNetSender(SenderBase):
    artnet_ip = None

    def __init__(self, data_senders: dict[str, SmSender], fixtures: list):
        SenderBase.__init__(self, data_senders, fixtures)
        self.artnet_ip = self.artnet_ip if self.artnet_ip is not None else "127.0.0.1"
        self.senders: list[StupidArtnet] = []
        self.fixtures_in_universe: dict[int, Set[Fixture]] = self._split_fixtures_in_universes()
        self.senders = self._get_senders_for_universes()


    def delete(self):
        super().delete()
        for sender in self.senders:
            sender.blackout()
            sender.close()
        del self.fixtures_in_universe

    def _split_fixtures_in_universes(self) -> dict[int, Set[Fixture]]:
        universes: dict[int, Set[Fixture]] = {}
        for universe in {fixture.dmx_universe for fixture in self.fixtures}:
            fixtures_in_universe = [fixture for fixture in self.fixtures if fixture.dmx_universe == universe]
            universes[universe] = set(fixtures_in_universe)
        return universes

    def send(self, dmx_values: list[DmxSignal]):
        for sender in self.senders:
            for frame in dmx_values:
                if frame.universe != sender.universe:
                    continue
                for channel_value in frame.channel_values:
                    sender.set_single_value(channel_value.channel, channel_value.value)
        for sender in self.senders:
            sender.show()


    @staticmethod
    def add_command_line_arguments(parser: argparse) -> argparse:
        parser.add_argument("--artnet-ip", dest='artnet_ip', required=True, type=lambda x: is_valid_ip(parser, x),
                            help="IP of the artnet server")

    @classmethod
    def apply_command_line_arguments(cls, args: argparse.Namespace):
        cls.artnet_ip = args.artnet_ip

    def _get_senders_for_universes(self):
        senders = []
        for universe, fixtures in self.fixtures_in_universe.items():
            if len(fixtures) == 0:
                logging.warning(f"No fixtures in universe {universe}, skipping")
                continue
            senders.append(
                StupidArtnet(universe=universe, target_ip=self.artnet_ip, broadcast=True, artsync=True))
        return senders
