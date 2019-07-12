"""
Module defining the protocol for sending and receiving
data between Endpoint applications.
"""
from msg import Msg, MsgType
import struct


NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
LEN_PREF_FMT = 'H'  # Length-prefix formatting
MSG_TYPE_FMT = 'B'  # Msg type flag formatting
# TODO: Add checksum into the header
HEADER_FMT = NET_FMT + LEN_PREF_FMT + MSG_TYPE_FMT  # Msg 'header' format

LEN_PREF_SZ_BYTES \
    = struct.calcsize(LEN_PREF_FMT)  # Bytes alloted for length prefix
HEADER_SZ_BYTES   \
    = struct.calcsize(HEADER_FMT)    # Size of msg 'header'

variable_data_fmt = '%ds'  # Format for variable message data
pack_fmt = HEADER_FMT + variable_data_fmt  # Packing format
unpack_fmt = HEADER_FMT + variable_data_fmt  # Unpacking format


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

    return Msg(MsgType(raw_msg_type), payload)


# Unit Testing
if __name__ == '__main__':
    # Construct message
    mt = MsgType.ENDPOINT_CONNECTION_BROADCAST
    data = 'this is a payload'.encode()
    message = Msg(mt, data)

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
