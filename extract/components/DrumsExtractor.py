import logging
import time

from extract.ExtractorBase import ExtractorBase
from shared.fixture.ChannelType import ChannelType as ct
from shared.fixture.ChannelValue import ChannelValue
from shared.fixture.FixtureSignal import FixtureSignal
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver


def normalize_fade_by_loudness(loudness, min_value=10, max_value=30):
    """
    Normalizes fade control to a value between 0 and 254,
    where the fade is inverse proportional to the loudness, with a threshold of 10 for silence.
     - If loudness is 0-10, fade is 254 (full fade)
     - If loudness is above 10, fade decreases linearly to 0 as loudness increases to 100.
     - At loudness 100 or above, fade is 0 (no fade).
    """
    if loudness < min_value:
        return 40

    if loudness >= max_value:
        return 0

    return min(int((1 - ((loudness - min_value) / (max_value - min_value))) * 40), 40)


def normalize_loudness(loudness, min_value=10, max_value=100):
    """
    Normalizes loudness to a value between 0 and 254,
    where 10 is the threshold for silence and
    everything above 10 scales linearly.
    """
    if loudness < min_value:
        return 20

    if loudness >= max_value:
        return 255

    scaled = (loudness - min_value) / (max_value - min_value)
    return min(int(scaled * 255) * 2, 255)


class DrumsExtractor(ExtractorBase):
    def __init__(self, data_senders):
        ExtractorBase.__init__(self, data_senders)
        self.rgb_receiver = NumpyArrayReceiver(data_senders.get("drums_rgb_image"))
        self.bass_loudness_receiver = NumpyArrayReceiver(data_senders.get("stem_loudness_drums"))

    def get_relevant_fixtures(self):
        return [self.fixtures[0]]

    async def run_procedure(self):
        rbg_data = self.rgb_receiver.read_on_update()
        loudness = self.bass_loudness_receiver.read_last()

        self.start_time = time.time()
        fixture_values = []
        for fixture in self.relevant_fixtures:
            channel_values = []
            rgb_values = rbg_data[fixture.position[0], fixture.position[1]]
            for dmx_address in fixture.dmx_addresses:
                if dmx_address[1] == ct.COLOR_RED:
                    channel_values.append(
                        ChannelValue(dmx_address[0], int(rgb_values[0])))
                elif dmx_address[1] == ct.COLOR_GREEN:
                    channel_values.append(
                        ChannelValue(dmx_address[0], int(rgb_values[1])))
                elif dmx_address[1] == ct.COLOR_BLUE:
                    channel_values.append(
                        ChannelValue(dmx_address[0], int(rgb_values[2])))
                elif dmx_address[1] == ct.CONTROL_DIMMER:
                    channel_values.append(
                        ChannelValue(dmx_address[0], normalize_loudness(loudness))
                    )
                elif dmx_address[1] == ct.CONTROL_FADE:
                    channel_values.append(
                        ChannelValue(dmx_address[0], normalize_fade_by_loudness(loudness))
                    )
            fixture_values.append((fixture, channel_values))
            self.fixture_signal_queue_sender.update(FixtureSignal(self.__class__.__name__, fixture, channel_values))
