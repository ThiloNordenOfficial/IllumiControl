import asyncio
import time
from abc import abstractmethod

from shared import StatisticWriter


class Runner(StatisticWriter):
    def run(self):
        asyncio.run(self._run_until_shutdown())

    async def _run_until_shutdown(self):
        while not self.kill_event.is_set():
            start_time = time.time()
            self.run_procedure()
            if self.statistics_are_active:
                self.write_statistics(time.time() - start_time)
        self.delete()


    @abstractmethod
    def run_procedure(self):
        pass

    extract = abstractmethod(run_procedure)