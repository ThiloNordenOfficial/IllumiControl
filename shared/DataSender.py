from abc import abstractmethod

from shared.shared_memory.NumpyArraySender import NumpyArraySender
from shared.shared_memory.Sender import Sender


class DataSender(object):

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, Sender]:
        pass

    get_data_senders = abstractmethod(get_outbound_data_senders)
