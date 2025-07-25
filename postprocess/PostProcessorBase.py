from abc import abstractmethod

from shared.fixture.DmxSignal import DmxSignal
from shared.fixture.FixtureSignal import FixtureSignal
from shared.runner.PostTimeRunner import PostTimeRunner


def is_list_of_type(obj, typ):
    return isinstance(obj, list) and all(isinstance(item, typ) for item in obj)


class PostProcessorBase(PostTimeRunner):

    async def run_after_processing(self, *args, **kwargs):
        if not (isinstance(args[0], list) and all(isinstance(x, FixtureSignal) for x in args[0])):
            raise ValueError("No fixture signals provided")
        if not (isinstance(args[1], list) and all(isinstance(x, DmxSignal) for x in args[1])):
            raise ValueError("No DMX signals provided")
        fixture_signals: list[FixtureSignal] = args[0]
        dmx_signals: list[DmxSignal] = args[1]
        return await self.run_after(fixture_signals, dmx_signals)

    @abstractmethod
    async def run_after(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        pass

    abstractmethod(run_after)
