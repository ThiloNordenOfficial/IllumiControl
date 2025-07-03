from abc import abstractmethod

from shared import DataSender
from shared.shared_memory.Sender import Sender


class IngestBase(DataSender):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, Sender]:
        pass
    abstractmethod(get_outbound_data_senders)