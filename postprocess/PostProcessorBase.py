from abc import abstractmethod

from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal
from shared.runner.PostTimeRunner import PostTimeRunner


class PostProcessorBase(PostTimeRunner):

    async def run_after_processing(self, *args, **kwargs):
        if not args or not isinstance(args[0], list):
            raise ValueError("No fixture signals provided")
        if not args or not isinstance(args[1], list):
            raise ValueError("No DMX signals provided")
        fixture_signals: list[FixtureSignal] = args[0]
        dmx_signals: list[DmxSignal] = args[1]
        return await self.run_after(fixture_signals, dmx_signals)

    @abstractmethod
    async def run_after(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        pass

    abstractmethod(run_after)
