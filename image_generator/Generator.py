import asyncio
import logging
from abc import abstractmethod
from typing import final

from shared.shared_memory.NumpyArraySender import NumpyArraySender


class Generator(object):
    def __init__(self, inbound_data_senders: dict[str, NumpyArraySender], height: int, width: int, depth: int):
        self.inbound_data_senders = inbound_data_senders
        self.height = height
        self.width = width
        self.depth = depth

    @abstractmethod
    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        pass

    get_data_senders = abstractmethod(get_outbound_data_senders)

    @final
    def generate(self):
        asyncio.run(self._generate())

    @abstractmethod
    async def _generate(self):
        pass
    _generate = abstractmethod(_generate)