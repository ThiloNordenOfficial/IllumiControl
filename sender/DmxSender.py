import itertools
import logging
from typing import Set

from stupidArtnet import StupidArtnet

from shared.fixture import Fixture
from shared import TimingReceiver, DmxQueueUser
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class DmxSender(TimingReceiver, DmxQueueUser):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], artnet_server_ip, fixtures: list[Fixture]):
        TimingReceiver.__init__(self, inbound_data_senders)
        DmxQueueUser.__init__(self)

        self.senders = []
        self.fixtures_in_universe: dict[int, Set[Fixture]] = {}
        for universe in {fixture.dmx_universe for fixture in fixtures}:
            self.senders.append(
                StupidArtnet(universe=universe, target_ip=artnet_server_ip, broadcast=True, artsync=True))
            fixtures_in_universe = [fixture for fixture in fixtures if fixture.dmx_universe == universe]
            self.fixtures_in_universe[universe] = set(fixtures_in_universe)

    def delete(self):
        super().delete()
        self.dmx_queue.close()
        for sender in self.senders:
            sender.blackout()
            sender.close()
        del self.fixtures_in_universe

    def run(self):
        for sender in self.senders:
            sender.start()

        while not self.kill_event.is_set():
            # No need to set timeouts, because sending the frame after new data is available, is last possible timing
            self.timing_receiver.read_on_update()
            dmx_frames = []
            while self.dmx_queue.qsize() != 0:
                dmx_frames.append(self.dmx_queue.get())
            dmx_frame = list(itertools.chain(*dmx_frames))
            for sender in self.senders:
                logging.debug(F"Setting Frames for universe {sender.universe}")
                for frame in dmx_frame:
                    logging.debug(F"{frame}")
                    sender.set_single_value(frame.channel, frame.value)
                sender.show()
        self.delete()
