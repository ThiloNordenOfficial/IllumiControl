from abc import abstractmethod

from shared import NumpyArrayReceiver
from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.Fixture import Fixture


class SenderBase():
    def __init__(self, data_senders: dict[str, 'SmSender'], fixtures: list[Fixture]):
        super().__init__()
        self.fixtures = fixtures
        self.post_processor_finished_receiver = NumpyArrayReceiver(data_senders.get("post_processing_finished"))

    @abstractmethod
    def send(self, dmx_values: list[DmxSignal]):
        pass

    abstractmethod(send)
