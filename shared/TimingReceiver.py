from shared import GracefulKiller
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.SmSender import SmSender


class TimingReceiver(GracefulKiller):

    def __init__(self, inbound_data_senders: dict[str, SmSender]):
        self.timing_receiver = NumpyArrayReceiver(inbound_data_senders.get("timing-data"))

    def delete(self):
        self.timing_receiver.close()
