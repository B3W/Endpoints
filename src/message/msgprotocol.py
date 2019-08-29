"""
Module defining the protocol for serializing and deserializing messages.
"""
from message import msg
import struct


NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
LEN_PREF_FMT = 'H'  # Length-prefix formatting (2 bytes alloted)
MSG_TYPE_FMT = 'B'  # Msg type flag formatting (1 byte alloted)
MSG_HEADER_FMT = NET_FMT + LEN_PREF_FMT + MSG_TYPE_FMT  # Msg 'header' format

LEN_PREF_SZ_BYTES \
    = struct.calcsize(LEN_PREF_FMT)  # Bytes alloted for length prefix
HEADER_SZ_BYTES   \
    = struct.calcsize(MSG_HEADER_FMT)    # Size of msg 'header'

variable_data_fmt = '%ds'  # Format for variable message data

# TODO: Add checksum onto end of packet

pack_fmt = MSG_HEADER_FMT + variable_data_fmt  # Packing format
unpack_fmt = MSG_HEADER_FMT + variable_data_fmt  # Unpacking format


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
    payload_sz = len(byte_data) - HEADER_SZ_BYTES
    dynamic_fmt = unpack_fmt % (payload_sz)

    msg_len, raw_msg_type, payload = struct.unpack(dynamic_fmt, byte_data)

    return msg.construct(msg.MsgType(raw_msg_type), payload)


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

    # Deserialize message
    deserialized_msg = deserialize(serialized_msg)

    print('Message Post-deserialization')
    print(deserialized_msg)
