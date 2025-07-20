from shared import GracefulKiller
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.SmSender import SmSender


class TimingReceiver(GracefulKiller):

    def __init__(self, data_senders: dict[str, SmSender]):
        self.timing_receiver = NumpyArrayReceiver(data_senders.get("timing-data"))

    def delete(self):
        self.timing_receiver.close()
