from abc import abstractmethod

from shared.shared_memory.SmSender import SmSender


class DataSender:

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, SmSender]:
        pass

