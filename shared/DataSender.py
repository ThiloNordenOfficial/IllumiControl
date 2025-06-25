from abc import abstractmethod

from shared.shared_memory.NumpyArraySender import NumpyArraySender


class DataSender(object):

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        pass

    get_data_senders = abstractmethod(get_outbound_data_senders)
