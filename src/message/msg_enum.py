"""
Module defining enum for different supported message types.
"""
from enum import Enum, unique


@unique
class MsgEnum(Enum):
    """
    Class representing an enum for supported message types.
    """
    # Specifying integer type instead of auto necessary to
    # know the format for struct.pack/struct.unpack
    DISCOVERY_POLL = 1
    DISCOVERY_RESP = 2
    COMMUNICATION = 3
    ACKNOWLEDGEMENT = 4
