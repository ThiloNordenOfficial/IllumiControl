import asyncio
import time
from abc import abstractmethod
from typing import final

from shared import StatisticWriter
from shared.shared_memory import SmSender, TimingReceiver


class PostTimeRunner(TimingReceiver, StatisticWriter):
    def __init__(self, data_senders: dict[str, 'SmSender']):
        TimingReceiver.__init__(self, data_senders)
        StatisticWriter.__init__(self)

    @final
    def run(self, *args, **kwargs):
        return asyncio.run(self._run(*args, **kwargs))

    @final
    async def _run(self, *args, **kwargs):
        start_time = time.time()
        return_value = await self.run_after_processing(*args, **kwargs)
        time_taken = time.time() - start_time
        self.write_statistics_time(time_taken)
        return return_value

    @abstractmethod
    async def run_after_processing(self, *args, **kwargs):
        pass

    abstractmethod(run_after_processing)
