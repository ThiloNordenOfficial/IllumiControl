from abc import abstractmethod

from shared import DataSender
from shared.runner.Runner import Runner
from shared.shared_memory.Sender import Sender


class AnalyserBase(DataSender, Runner):
    def __init__(self, inbound_data_senders: dict[str, Sender]):
        super().__init__()
        self.inbound_data_senders = inbound_data_senders

    @abstractmethod
    def delete(self):
        del self.inbound_data_senders

    delete = abstractmethod(delete)
