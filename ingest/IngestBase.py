from abc import abstractmethod

from shared import DataSender
from shared.shared_memory.SmSender import SmSender


class IngestBase(DataSender):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        pass
    abstractmethod(get_outbound_data_senders)