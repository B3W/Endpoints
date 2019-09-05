"""
Module defining message structure and message types.
"""
from shared import config as c
import enum
from network import netid


@enum.unique
class MsgType(enum.Enum):
    """
    Enum of supported message types.
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
    ENDPOINT_COMMUNICATION_ACK = 5

    NUM_MSG_TYPES = ENDPOINT_COMMUNICATION_ACK + 1


class Msg(object):
    """
    Structure representing message to be sent between Endpoints
    """
    def __init__(self, msg_type, payload):
        """
        Initialization for message

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
        return '<%s type:%s payload:%s>' \
            % (self.__class__.__name__, self.msg_type.name, self.payload)

    def __str__(self):
        return '\'%s\' Object\nType:%s\nPayload:%s\nLen:%d' \
            % (self.__class__.__name__, self.msg_type.name,
               self.payload, self.__len__())


# Used for validation of MsgType
CONNECTION_MSG_TYPES = [MsgType.ENDPOINT_CONNECTION_BROADCAST,
                        MsgType.ENDPOINT_CONNECTION_RESPONSE,
                        MsgType.ENDPOINT_DISCONNECTED_BROADCAST]

COMMUNICATION_MSG_TYPES = [MsgType.ENDPOINT_COMMUNICATION,
                           MsgType.ENDPOINT_COMMUNICATION_ACK]


def construct(msg_type, payload=b''):
    '''
    Constructs appropriate message based on given arguments
    '''
    if msg_type in CONNECTION_MSG_TYPES:
        # Payload is a NetID object
        byte_data = payload.tobytes()

        return Msg(msg_type, byte_data)

    elif msg_type in COMMUNICATION_MSG_TYPES:
        # Payload is a string or bytes object
        try:
            byte_data \
                = payload.encode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))

        except AttributeError:
            # Bytes object so no need to encode
            byte_data = payload

        return Msg(msg_type, byte_data)

    else:
        raise ValueError('%s is not a supported MsgType' % (str(msg_type)))


def decode_payload(message):
    '''
    Returns the payload decoded to the correct object
    '''
    if message.msg_type in CONNECTION_MSG_TYPES:
        # Payload is a NetID object
        return netid.frombytes(message.payload)

    elif message.msg_type in COMMUNICATION_MSG_TYPES:
        # Payload is a string or bytes object
        return message.payload.decode(
            c.Config.get(c.ConfigEnum.BYTE_ENCODING))

    else:
        raise ValueError('%s is not a supported MsgType'
                         % (str(message.msg_type)))


# Unit Testing
def test():
    # Construct message
    mt = MsgType.ENDPOINT_COMMUNICATION
    data = 'this is data'

    message = construct(mt, data)

    # Check relevant info
    print(repr(message))
    print(message)
    print()

    data = decode_payload(message)
    print('Decoded message payload:')
    print(data)
