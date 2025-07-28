import asyncio
import logging
import time
from abc import abstractmethod
from typing import final

from shared.runner.Runner import Runner
from shared.shared_memory import SmSender, TimingReceiver


class TimedRunner(Runner, TimingReceiver):
    def __init__(self, data_senders: dict[str, SmSender]):
        TimingReceiver.__init__(self, data_senders)
        Runner.__init__(self)
        self.complexity = 1
        self._max_complexity = 100000000
        self._times_without_complexity_adjustment = 0

    def delete(self):
        super().delete()
        self.timing_receiver.close()

    def adjust_complexity(self, success: bool):
        if success:
            self.complexity = min(100, self.complexity + 1)
            if self._max_complexity >= self.complexity:
                self._times_without_complexity_adjustment += 1
            else:
                self._times_without_complexity_adjustment = 0
        else:
            self.complexity = max(1, int(self.complexity * 0.5))
            self._times_without_complexity_adjustment = 0
            logging.debug(f"Decreased complexity of {self.__class__.__name__} to {self.complexity}")

    @abstractmethod
    async def run_procedure(self):
        pass

    abstractmethod(run_procedure)

    @final
    def run(self):
        asyncio.run(self._run_until_shutdown())

    @final
    async def _run_until_shutdown(self):
        while not self.kill_event.is_set():
            max_time = float(self.timing_receiver.read_on_update()[0])
            start_time = time.time()
            try:
                await asyncio.wait_for(self.run_procedure(), timeout=max_time)
                self.adjust_complexity(True)
                time_taken = time.time() - start_time
                self.write_statistics_time(time_taken)
                await asyncio.sleep(max_time-time_taken)
            except asyncio.TimeoutError:
                logging.warning(
                    F"Dropped {self.__class__.__name__} step due to not finishing in time ({max_time}s), will adjust complexity")
                self.adjust_complexity(False)

        self.delete()
