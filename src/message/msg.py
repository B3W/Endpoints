"""
Module defining message structure.
"""
from enum import Enum, unique


@unique
class MsgType(Enum):
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
    ENDPOINT_COMM = 4
    # Acknowledgement that communication succeeded
    ENDPOINT_COMM_ACKNOWLEDGEMENT = 5

    NUM_MSG_TYPES = ENDPOINT_COMM_ACKNOWLEDGEMENT + 1


class Msg(object):
    """
    Message class.
    """

    def __init__(self, msg_type, payload):
        """
        'Constructor' for message

        :param msg_type: Type of message denoted given by MsgType enum
        :param payload: Message data as 'bytes' object
        """
        self.msg_type = msg_type
        self.payload = payload

    def __len__(self):
        """
        Gets the length of the message

        :returns: Length of message payload
        """
        return len(self.payload)

    def __repr__(self):
        return '<Msg type:%s payload:%s>' % \
            (self.msg_type.name, self.payload)

    def __str__(self):
        return '\'Msg\' Object\nType:%s\nPayload:%s\nLen:%d' % \
            (self.msg_type.name, self.payload, self.__len__())


# Unit Testing
if __name__ == '__main__':
    # Construct message
    mt = MsgType.ENDPOINT_COMM
    data = 'data'.encode()
    message = Msg(mt, data)

    # Check relevant info
    print(repr(message))
    print()
    print(message)
