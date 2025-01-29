from typing import Tuple, TypeGuard, List

from DmxChannelType import DmxChannelType
from FixtureType import FixtureType


def verify_dmx_address(dmx_address):
    # check if the dmx address is in the correct range
    if dmx_address[0][0] < 1 or dmx_address[0][0] > 512:
        raise ValueError("DMX address out of range")

    # check if every dmx address is continuous
    for i in range(1, len(dmx_address)):
        if dmx_address[i][0] != dmx_address[i - 1][0] + 1:
            raise ValueError("DMX addresses not continuous")

    # check if any ChannelTypes are duplicated
    if len(dmx_address) != len(set([x[1] for x in dmx_address])):
        raise ValueError("Duplicate ChannelTypes")

    # check if all ChannelTypes are valid
    for address in dmx_address:
        verify_dmx_channel_type(address[1])

def verify_dmx_channel_type(channel_type) -> TypeGuard[DmxChannelType]:
    try:
        DmxChannelType(channel_type)
        return True
    except KeyError:
        raise ValueError(f"Unknown channel type: {channel_type}")

def verify_fixture_type(fixture_type) -> TypeGuard[FixtureType]:
    try:
        FixtureType(fixture_type)
        return True
    except KeyError:
        raise ValueError(f"Unknown fixture type: {fixture_type}")

class Fixture:
    def __init__(self, fixture_id: int, fixture_type: str, dmx_universe: int,
                 dmx_addresses: List[Tuple[int, str]], position: Tuple[int, int, int]):
        self.fixture_id = fixture_id
        verify_fixture_type(fixture_type)
        self.type: FixtureType = FixtureType(fixture_type)
        self.dmx_universe = dmx_universe
        verify_dmx_address(dmx_addresses)
        self.dmx_addresses: [Tuple[int, DmxChannelType]] = [(addr, DmxChannelType(ch_type)) for addr, ch_type in dmx_addresses]
        self.position = position

    def __str__(self):
        return f"Fixture Id: {self.fixture_id}, Type: {self.type}, Universe: {self.dmx_universe}, Addresses: {self.dmx_addresses}, Position: {self.position}"

    def __repr__(self):
        return self.__str__()
