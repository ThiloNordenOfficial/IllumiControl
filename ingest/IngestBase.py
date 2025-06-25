from abc import abstractmethod

from shared import DataSender
from shared.Runner import Runner
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class IngestBase(DataSender, Runner):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender]):
        super().__init__()
        self.inbound_data_senders = inbound_data_senders

    @abstractmethod
    def delete(self):
        del self.inbound_data_senders

    delete = abstractmethod(delete)
