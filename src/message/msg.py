'''
Module defining message structure and message types.
'''
import config as c
import enum
import netid as netid
import timeutils


@enum.unique
class MsgType(enum.Enum):
    '''Enum of supported message types'''
    # Specifying integer type instead of auto for
    # struct.pack/struct.unpack formatting scheme

    # Message broadcast when a new Endpoint connects to LAN
    ENDPOINT_CONNECTION_BROADCAST = 1
    # Message for reporting GUID to a new connection
    ENDPOINT_CONNECTION_START = 2
    # Message broadcast to connected Enpoints when an Endpoint disconnects
    ENDPOINT_DISCONNECTION = 3
    # Message for sending user communication between Endpoints
    ENDPOINT_TEXT_COMMUNICATION = 4
    # Acknowledgement that communication succeeded
    ENDPOINT_COMMUNICATION_ACK = 5

    NUM_MSG_TYPES = ENDPOINT_COMMUNICATION_ACK + 1


class Msg(object):
    '''Structure representing message to be sent between Endpoints'''
    TIMESTAMP_SZ_BYTES = 19  # Length of ISO formatted time string

    def __init__(self, msg_type, payload, timestamp=None):
        """
        Initialization for message

        :param msg_type: Type of message denoted given by MsgType enum
        :param payload: Message data as 'bytes' object
        :param timestamp: Optional timestamp, if None current timestamp used
        """
        if timestamp is None:
            self.timestamp = timeutils.get_iso_timestamp()
        else:
            self.timestamp = timestamp

        self.msg_type = msg_type
        self.payload = payload

    def __repr__(self):
        return '<%s type:%s timestamp:%s payload:%s>' \
            % (self.__class__.__name__,
               self.msg_type.name, self.timestamp, self.payload)

    def __str__(self):
        return '<\'%s\' Object Type:%s Timestamp:%s Payload:%s>' \
            % (self.__class__.__name__,
               self.msg_type.name, self.timestamp, self.payload)


# Used for validation of MsgType
CONNECTION_MSG_TYPES = [MsgType.ENDPOINT_CONNECTION_BROADCAST,
                        MsgType.ENDPOINT_CONNECTION_START,
                        MsgType.ENDPOINT_DISCONNECTION]

COMMUNICATION_MSG_TYPES = [MsgType.ENDPOINT_TEXT_COMMUNICATION,
                           MsgType.ENDPOINT_COMMUNICATION_ACK]


def encode_payload(msg_type, payload):
    '''Encodes the message's payload'''
    if msg_type in CONNECTION_MSG_TYPES:
        # Payload is a NetID object
        return netid.tobytes(payload)

    elif msg_type in COMMUNICATION_MSG_TYPES:
        # Payload is a string or bytes object
        try:
            return payload.encode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))

        except AttributeError:
            # Bytes object so no need to encode
            pass

    else:
        raise ValueError(f'{str(msg_type)} is not a supported MsgType')

    return payload


def decode_payload(msg_type, raw_payload):
    '''Returns the payload decoded to the correct object'''
    if msg_type in CONNECTION_MSG_TYPES:
        # Payload is a NetID object
        return netid.frombytes(raw_payload)

    elif msg_type in COMMUNICATION_MSG_TYPES:
        # Payload is a string or bytes object
        return raw_payload.decode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))

    else:
        raise ValueError('%s is not a supported MsgType'
                         % (str(msg_type)))


# Unit Testing
def test():
    # Construct message
    mt = MsgType.ENDPOINT_TEXT_COMMUNICATION
    data = 'this is data'

    message = Msg(mt, data)

    # Check relevant info
    print(repr(message))
    print(message)
    print()

    enc_payload = encode_payload(message.msg_type, message.payload)
    data = decode_payload(message.msg_type, enc_payload)
    print('Decoded message payload:')
    print(data)
