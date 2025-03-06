from abc import abstractmethod

from shared.shared_memory.NumpyArraySender import NumpyArraySender


class Extractor(object):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], fixtures):
        self.inbound_data_senders = inbound_data_senders
        self.fixtures = fixtures

    @abstractmethod
    def extract(self):
        pass

    extract = abstractmethod(extract)
