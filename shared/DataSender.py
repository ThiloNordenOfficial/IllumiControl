from abc import abstractmethod

from shared.shared_memory.SmSender import SmSender


class DataSender(object):

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        pass

    get_data_senders = abstractmethod(get_outbound_data_senders)
