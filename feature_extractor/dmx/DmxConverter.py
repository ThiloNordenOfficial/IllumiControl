import itertools
import logging
from ipcqueue.posixmq import Queue
from stupidArtnet import StupidArtnet
from feature_extractor.fixture import Fixture
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class DmxConverter:
    def __init__(self, inbound_data_senders: [NumpyArraySender], artnet_server_ip, fixtures: [Fixture]):
        self.timing_receiver = NumpyArrayReceiver(inbound_data_senders['timing-data'])
        self.queue = Queue("/dmx_queue")
        self.senders = []
        self.fixtures_in_universe: dict[(int, [Fixture])] = {}
        for universe in set([fixture.dmx_universe for fixture in fixtures]):
            self.senders.append(
                StupidArtnet(universe=universe, target_ip=artnet_server_ip, broadcast=True, artsync=True))
            fixtures_in_universe = [fixture for fixture in fixtures if fixture.dmx_universe == universe]
            self.fixtures_in_universe[universe] = fixtures_in_universe

    def send_dmx_frame(self):
        pass

    def run(self):
        for sender in self.senders:
            sender.start()

        while True:
            # No need to set timeouts, because sending the frame after new data is available, is last possible timing
            self.timing_receiver.read_on_update()
            dmx_frames = []
            while not self.queue.qsize() == 0:
                dmx_frames.append(self.queue.get())
            dmx_frame = list(itertools.chain(*dmx_frames))
            for sender in self.senders:
                logging.debug(F"Setting Frame for universe: {dmx_frame}, {sender.universe}")
                for frame in dmx_frame:
                    sender.set_single_value(frame.channel, frame.value)
                sender.show()