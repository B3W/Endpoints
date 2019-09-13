"""
Module defining the protocol for serializing and deserializing messages.
"""
from message import msg
import struct


_g_NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
_g_LEN_PREF_FMT = 'H'  # Length-prefix formatting (2 bytes alloted)
_g_MSG_TYPE_FMT = 'B'  # Msg type flag formatting (1 byte alloted)

# Bytes alloted for length prefix
g_LEN_PREF_SZ_BYTES = struct.calcsize(_g_LEN_PREF_FMT)
# Bytes alloted for message type field
g_MSG_TYPE_SZ_BYTES = struct.calcsize(_g_MSG_TYPE_FMT)

# Msg 'header' format
g_MSG_HEADER_FMT = _g_NET_FMT + _g_LEN_PREF_FMT + _g_MSG_TYPE_FMT
# Size of msg 'header'
g_HEADER_SZ_BYTES = struct.calcsize(g_MSG_HEADER_FMT)

variable_data_fmt = '%ds'  # Format for variable message data

# TODO: Add checksum onto end of packet

pack_fmt = g_MSG_HEADER_FMT + variable_data_fmt  # Packing format
unpack_fmt = g_MSG_HEADER_FMT + variable_data_fmt  # Unpacking format


def serialize(message):
    """
    Serializes message for sending over wire

    :param message: message to send

    :returns: Bytes object representing message to send
    """
    dynamic_fmt = pack_fmt % (len(message))
    msg_sz = struct.calcsize(dynamic_fmt)

    return struct.pack(dynamic_fmt,
                       msg_sz,
                       message.msg_type.value,
                       message.payload)


def deserialize(byte_data):
    """
    Converts byte data into message object

    :param byte_data: bytes to convert to message

    :returns: Message object
    """
    # Validate byte_data
    if not is_valid_msg(byte_data):
        raise ValueError('Attempt to deserialize invalid message')

    payload_sz = len(byte_data) - g_HEADER_SZ_BYTES
    dynamic_fmt = unpack_fmt % (payload_sz)

    msg_len, raw_msg_type, payload = struct.unpack(dynamic_fmt, byte_data)

    return msg.Msg(msg.MsgType(raw_msg_type), payload)


def __get_raw_msg_type(byte_data):
    '''
    Extracts the raw message type from the byte data

    :param byte_data: Bytes representing message
    :returns: Raw message type as integer
    '''
    # Message type location within bytes
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


def is_connect_broadcast(byte_data):
    '''
    Checks whether or not bytes represent a connection broadcast message

    :param byte_data: Bytes to check
    :returns: True if bytes are broadcast connect message, False otherwise
    '''
    is_msg_type = False

    if is_valid_msg(byte_data):
        # Check if message is a connection broadcast
        msg_type = msg.MsgType(__get_raw_msg_type(byte_data))

        if msg_type == msg.MsgType.ENDPOINT_CONNECTION_BROADCAST:
            is_msg_type = True

    return is_msg_type


def is_disconnection(byte_data):
    '''
    Checks whether or not bytes represent a disconnection message

    :param byte_data: Bytes to check
    :returns: True if bytes are disconnect message, False otherwise
    '''
    is_msg_type = False

    if is_valid_msg(byte_data):
        # Check if message is a connection broadcast
        msg_type = msg.MsgType(__get_raw_msg_type(byte_data))

        if msg_type == msg.MsgType.ENDPOINT_DISCONNECTION:
            is_msg_type = True

    return is_msg_type


def is_broadcast_response(byte_data):
    '''
    Checks whether or not bytes represent a broadcast response message

    :param byte_data: Bytes to check
    :returns: True if bytes are broadcast response message, False otherwise
    '''
    is_msg_type = False

    if is_valid_msg(byte_data):
        # Check if message is a connection broadcast
        msg_type = msg.MsgType(__get_raw_msg_type(byte_data))

        if msg_type == msg.MsgType.ENDPOINT_CONNECTION_RESPONSE:
            is_msg_type = True

    return is_msg_type


# Unit Testing
def test():
    # Construct message
    mt = msg.MsgType.ENDPOINT_COMMUNICATION
    data = 'this is a payload'.encode()

    message = msg.construct(mt, data)

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

    if is_connect_broadcast(serialized_msg):
        print('Broadcast Connection!')
    else:
        print('Non Broadcast Connection')

    if is_disconnection(serialized_msg):
        print('Broadcast Disconnection!')
    else:
        print('Non Broadcast Disconnection')

    if is_broadcast_response(serialized_msg):
        print('Broadcast Connection Response!')
    else:
        print('Non Broadcast Response')

    print()

    # Deserialize message
    deserialized_msg = deserialize(serialized_msg)

    print('Message Post-deserialization')
    print(deserialized_msg)
