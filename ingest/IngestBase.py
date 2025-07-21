from abc import abstractmethod

from shared import DataSender
from shared.shared_memory.SmSender import SmSender


class IngestBase(DataSender):

    def __init__(self):
        DataSender.__init__(self)

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        pass
    abstractmethod(get_outbound_data_senders)