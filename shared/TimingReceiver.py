from shared import GracefulKiller
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class TimingReceiver(GracefulKiller):

    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender]):
        self.timing_receiver = NumpyArrayReceiver(inbound_data_senders.get("npa-timing-data"))

    def delete(self):
        self.timing_receiver.close()
