from typing import Tuple, TypeGuard, List

from shared.fixture.FixtureType import FixtureType
from shared.fixture.ChannelType import ChannelType


class Fixture:
    def __init__(self, fixture_id: int, fixture_type: str, dmx_universe: int,
                 dmx_addresses: List[Tuple[int, str]], position: Tuple[int, int, int]):
        verify_initialization_data(fixture_type, dmx_universe, dmx_addresses, position)
        self.fixture_id: int = fixture_id
        self.type: FixtureType = FixtureType(fixture_type)
        self.dmx_universe: int = dmx_universe
        self.dmx_addresses: [Tuple[int, ChannelType]] = [(addr, ChannelType(ch_type)) for addr, ch_type in
                                                         dmx_addresses]
        self.position: Tuple[int, int, int] = position

    def __str__(self):
        return f"Fixture Id: {self.fixture_id}, Type: {self.type}, Universe: {self.dmx_universe}, Addresses: {self.dmx_addresses}, Position: {self.position}"

    def __repr__(self):
        return self.__str__()


def verify_initialization_data(fixture_type, dmx_universe, dmx_addresses, position):
    verify_fixture_type(fixture_type)
    verify_universe(dmx_universe)
    verify_dmx_address(dmx_addresses)
    verify_position(position)


def verify_dmx_address(dmx_address):
    # check if the dmx address is in the correct range
    if dmx_address[0][0] < 1 or dmx_address[0][0] > 512:
        raise ValueError("DMX address out of range")

    # check if every dmx address is continuous
    for i in range(1, len(dmx_address)):
        if dmx_address[i][0] != dmx_address[i - 1][0] + 1:
            raise ValueError("DMX addresses not continuous")

    # check if any ChannelTypes are duplicated
    if len(dmx_address) != len({x[1] for x in dmx_address}):
        raise ValueError("Duplicate ChannelTypes")

    # check if all ChannelTypes are valid
    for address in dmx_address:
        verify_dmx_channel_type(address[1])


def verify_dmx_channel_type(channel_type) -> TypeGuard[ChannelType]:
    try:
        ChannelType(channel_type)
        return True
    except KeyError:
        raise ValueError(f"Unknown channel type: {channel_type}")


def verify_fixture_type(fixture_type) -> TypeGuard[FixtureType]:
    try:
        FixtureType(fixture_type)
        return True
    except KeyError:
        raise ValueError(f"Unknown fixture type: {fixture_type}")


def verify_position(position):
    if len(position) != 3:
        raise ValueError("Position must be a 3-tuple")
    for i in position:
        if not isinstance(i, int):
            raise ValueError("Position must be a 3-tuple of integers")
        if i < 0:
            raise ValueError("Position must be positive integers")


def verify_universe(dmx_universe):
    if not 0 <= int(dmx_universe) <= 512:
        raise ValueError("Universe must be a number between 0 and 512")
