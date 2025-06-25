from extractor.ExtractorBase import ExtractorBase
from shared.fixture import ChannelType as ct
from shared.DmxChannelValue import DmxChannelValue
from shared.shared_memory.NumpyArrayReceiver import NumpyArrayReceiver
from shared.shared_memory.NumpyArraySender import NumpyArraySender


class RGBExtractor(ExtractorBase):
    def __init__(self, inbound_data_senders, fixtures):
        super().__init__(inbound_data_senders, fixtures)
        self.rgb_data_receiver = NumpyArrayReceiver(inbound_data_senders.get("RGB-image"))
        self.relevant_fixtures = [fixture for fixture in fixtures if fixture.dmx_addresses[1] == ct.COLOR_RED or
                                  ct.COLOR_GREEN or
                                  ct.COLOR_BLUE]

    def delete(self):
        super().delete()
        self.rgb_data_receiver.close()
        del self.relevant_fixtures

    def get_outbound_data_senders(self) -> dict[str, NumpyArraySender]:
        return {}

    def run_procedure(self):
        rbg_data = self.rgb_data_receiver.read_on_update()
        dmx_frame = []
        for fixture in self.relevant_fixtures:
            rgb_values = rbg_data[fixture.position[0], fixture.position[1], fixture.position[2]]
            for dmx_address in fixture.dmx_addresses:
                if dmx_address[1] == ct.COLOR_RED:
                    dmx_frame.append(
                        DmxChannelValue(fixture.fixture_id, dmx_address[0], int(rgb_values[0])))
                elif dmx_address[1] == ct.COLOR_GREEN:
                    dmx_frame.append(
                        DmxChannelValue(fixture.fixture_id, dmx_address[0], int(rgb_values[1])))
                elif dmx_address[1] == ct.COLOR_BLUE:
                    dmx_frame.append(
                        DmxChannelValue(fixture.fixture_id, dmx_address[0], int(rgb_values[2])))
        self.dmx_queue.put(dmx_frame)
