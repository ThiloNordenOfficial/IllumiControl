from abc import abstractmethod

from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.Fixture import Fixture
from shared.runner import PostTimeRunner
from shared.shared_memory import NumpyArrayReceiver


class SenderBase(PostTimeRunner):
    def __init__(self, data_senders: dict[str, 'SmSender'], fixtures: list[Fixture]):
        super().__init__(data_senders)
        self.fixtures = fixtures
        self.post_processor_finished_receiver = NumpyArrayReceiver(data_senders.get("post_processing_finished"))

    async def run_after_processing(self, *args, **kwargs):
        if not args or not isinstance(args[0], list) or not all(isinstance(x, DmxSignal) for x in args[0]):
            raise ValueError("No DMX values provided")
        dmx_values = args[0]
        return await self.run_after(dmx_values)

    @abstractmethod
    async def run_after(self, dmx_values: list[DmxSignal]):
        pass

    abstractmethod(run_after)
