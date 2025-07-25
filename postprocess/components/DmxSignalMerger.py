from postprocess.PostProcessorBase import PostProcessorBase
from shared.fixture import FixtureSignal, DmxSignal


class DmxSignalMerger(PostProcessorBase):
    def run_after(self, fixture_signals: list[FixtureSignal], dmx_signals: list[DmxSignal]) -> list[
        DmxSignal]:
        universe_map = {}
        for dmx_signal in dmx_signals:
            if dmx_signal.universe not in universe_map:
                universe_map[dmx_signal.universe] = []
            universe_map[dmx_signal.universe].extend(dmx_signal.channel_values)

        merged_signals = []
        for universe, channel_values in universe_map.items():
            if channel_values:
                merged_signals.append(DmxSignal(universe, channel_values))
        return merged_signals
