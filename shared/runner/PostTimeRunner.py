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
        await asyncio.sleep(float(self.timing_receiver.read_on_update()[0]))
        start_time = time.time()
        return_value = await self.run_after_processing(*args, **kwargs)
        time_taken = time.time() - start_time
        if self.statistics_are_active:
            self.write_statistics(time_taken)
        return return_value

    @abstractmethod
    async def run_after_processing(self, *args, **kwargs):
        pass

    abstractmethod(run_after_processing)
