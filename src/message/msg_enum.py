"""
Module defining enum for different supported message types.
"""
from enum import Enum, unique


@unique
class MsgEnum(Enum):
    """
    Class representing an enum for supported message types.
    """
    # Specifying integer type instead of auto for
    # struct.pack/struct.unpack formatting scheme

    # Message broadcast when a new Endpoint connects to LAN
    ENDPOINT_CONNECTION_BROADCAST = 1
    # Response to the new connection broadcast
    ENDPOINT_CONNECTION_RESPONSE = 2
    # Message broadcast to connected Enpoints when an Endpoint disconnects
    ENDPOINT_DISCONNECTED_BROADCAST = 3
    # Message for sending user communication between Endpoints
    ENDPOINT_COMMUNICATION = 4
    # Acknowledgement that communication succeeded
    ENDPOINT_COMM_ACKNOWLEDGEMENT = 5
