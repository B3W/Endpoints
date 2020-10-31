"""
Module defining the protocol for serializing and deserializing messages.
"""
import msg
import config as c
import struct


_g_NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
_g_LEN_PREF_FMT = 'H'  # Length-prefix formatting (2 bytes alloted)
_g_MSG_TYPE_FMT = 'B'  # Msg type flag formatting (1 byte alloted)
_g_TIMESTAMP_FMT = f'{msg.Msg.TIMESTAMP_SZ_BYTES}s'  # ISO timestamp formatting

# Bytes alloted for length prefix
g_LEN_PREF_SZ_BYTES = struct.calcsize(_g_LEN_PREF_FMT)
# Bytes alloted for message type field
g_MSG_TYPE_SZ_BYTES = struct.calcsize(_g_MSG_TYPE_FMT)

# Msg 'header' format
g_MSG_HEADER_FMT = _g_NET_FMT           \
                 + _g_LEN_PREF_FMT      \
                 + _g_MSG_TYPE_FMT      \
                 + _g_TIMESTAMP_FMT

# Size of msg 'header'
g_HEADER_SZ_BYTES = struct.calcsize(g_MSG_HEADER_FMT)

variable_data_fmt = '%ds'  # Format for variable message data

pack_fmt = g_MSG_HEADER_FMT + variable_data_fmt  # Packing format
unpack_fmt = g_MSG_HEADER_FMT + variable_data_fmt  # Unpacking format


def serialize(message):
    """
    Serializes message for sending over wire

    :param message: message to send

    :returns: Bytes object representing message to send
    """
    # Encode the timestamp and payload
    encoded_timestamp \
        = message.timestamp.encode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))

    encoded_payload = msg.encode_payload(message.msg_type, message.payload)

    # Construct packing format
    dynamic_fmt = pack_fmt % (len(encoded_payload))
    msg_sz = struct.calcsize(dynamic_fmt)

    return struct.pack(dynamic_fmt,
                       msg_sz,
                       message.msg_type.value,
                       encoded_timestamp,
                       encoded_payload)


def deserialize(byte_data):
    """
    Converts byte data into message object

    :param byte_data: bytes to convert to message

    :returns: Message object
    """
    # Validate byte_data
    if not is_valid_msg(byte_data):
        raise ValueError('Attempt to deserialize invalid message')

    # Calculate the size of the payload and construct unpacking format
    payload_sz = len(byte_data) - g_HEADER_SZ_BYTES
    dynamic_fmt = unpack_fmt % (payload_sz)

    # Unpack the binary data
    msg_len, raw_msg_type, raw_timestamp, raw_payload \
        = struct.unpack(dynamic_fmt, byte_data)

    msg_type = msg.MsgType(raw_msg_type)
    payload = msg.decode_payload(msg_type, raw_payload)
    timestamp = raw_timestamp.decode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))

    return msg.Msg(msg_type, payload, timestamp)


def __get_raw_msg_type(byte_data):
    '''
    Extracts the raw message type from the byte data

    :param byte_data: Bytes representing message
    :returns: Raw message type as integer
    '''
    # Message type location within byte data
    msg_type_start = g_LEN_PREF_SZ_BYTES
    msg_type_end = g_LEN_PREF_SZ_BYTES + g_MSG_TYPE_SZ_BYTES

    # Convert bytes to integer
    msg_type_bytes = byte_data[msg_type_start:msg_type_end]
    raw_msg_type = int.from_bytes(msg_type_bytes, 'big')

    return raw_msg_type


def is_valid_msg(byte_data):
    '''
    Validates whether or not bytes represent a message

    :param byte_data: Bytes to validate
    :returns: True if valid, False otherwise
    '''
    valid = False

    if len(byte_data) < g_HEADER_SZ_BYTES:
        # Message length check
        valid = False
    else:
        # Message type check
        raw_msg_type = __get_raw_msg_type(byte_data)

        try:
            # Message type check
            msg.MsgType(raw_msg_type)
            valid = True  # If we make it here MsgType is valid
        except ValueError:
            # Enum will throw ValueError if given MsgType invalid
            valid = False

    return valid


def decode_msgtype(byte_data):
    '''
    Determines the MsgType of the message represented by byte data

    :param byte_data: Bytes to check
    :returns: MsgType if bytes valid message, None otherwise
    '''
    msg_type = None

    if is_valid_msg(byte_data):
        msg_type = msg.MsgType(__get_raw_msg_type(byte_data))

    return msg_type


# Unit Testing
def test():
    # Construct message
    mt = msg.MsgType.ENDPOINT_TEXT_COMMUNICATION
    data = 'this is a payload'

    message = msg.Msg(mt, data)

    print('Message Pre-serialization')
    print(message)
    print()

    # Serialize message
    serialized_msg = serialize(message)

    print('Message Post-serialization')
    print(serialized_msg)
    print()

    # Check validation methods
    if not is_valid_msg(serialized_msg):
        raise ValueError('Unable to validate message during testing')

    msg_type = decode_msgtype(serialized_msg)
    print('Decoded MsgType: %s' % (msg_type))
    print()

    # Deserialize message
    deserialized_msg = deserialize(serialized_msg)

    print('Message Post-deserialization')
    print(deserialized_msg)
