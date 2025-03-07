import asyncio
from abc import abstractmethod
from typing import final

from shared.shared_memory.NumpyArraySender import NumpyArraySender


class Extractor(object):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], fixtures):
        self.inbound_data_senders = inbound_data_senders
        self.fixtures = fixtures

    @final
    def extract(self):
        asyncio.run(self._extract())

    @abstractmethod
    async def _extract(self):
        pass

    _extract = abstractmethod(_extract)
