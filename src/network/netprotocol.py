"""
Module defining protocol for serializing and deserializing NetPackets for
sending and receiving data between Endpoint applications.
"""
from message import msgprotocol
from network import netpacket as np
from shared import config as c
import struct
import sys

g_GUID_SZ_BYTES = 16  # GUIDs are 128-bit integers

_g_NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
_g_LEN_PREF_FMT = 'H'  # Length-prefix formatting (2 bytes alloted)
_g_SRC_ID_FMT = g_GUID_SZ_BYTES + 's'  # GUID as bytes
_g_DST_ID_FMT = g_GUID_SZ_BYTES + 's'  # GUID as bytes

# Bytes alloted for length prefix
g_LEN_PREF_SZ_BYTES = struct.calcsize(_g_LEN_PREF_FMT)
# Pkt 'header' format
g_MSG_HEADER_FMT = _g_NET_FMT + _g_LEN_PREF_FMT + _g_SRC_ID_FMT + _g_DST_ID_FMT
# Size of msg 'header'
g_HEADER_SZ_BYTES = struct.calcsize(g_MSG_HEADER_FMT)

variable_data_fmt = '%ds'  # Format for variable message data

pack_fmt = g_MSG_HEADER_FMT + variable_data_fmt  # Packing format
unpack_fmt = g_MSG_HEADER_FMT + variable_data_fmt  # Unpacking format


def serialize(packet):
    """
    Serializes packet for sending over wire

    :param packet: NetPacket to serialize

    :returns: Bytes object representing NetPacket to send
    """
    dynamic_fmt = pack_fmt % (len(packet))
    msg_sz = struct.calcsize(dynamic_fmt)

    src_guid_bytes = packet.src.to_bytes(g_GUID_SZ_BYTES,
                                         byteorder=sys.byteorder,
                                         signed=False)
    dst_guid_bytes = packet.dst.to_bytes(g_GUID_SZ_BYTES,
                                         byteorder=sys.byteorder,
                                         signed=False)

    return struct.pack(dynamic_fmt,
                       msg_sz,
                       src_guid_bytes,
                       dst_guid_bytes,
                       packet.msg_payload)


def deserialize(byte_data):
    """
    Converts byte data into NetPacket object

    :param byte_data: Bytes representing NetPacket

    :returns: NetPacket
    """
    # Validate byte_data
    if not is_valid_pkt(byte_data):
        raise ValueError('Attempt to deserialize invalid packet')

    payload_sz = len(byte_data) - g_HEADER_SZ_BYTES
    dynamic_fmt = unpack_fmt % (payload_sz)

    pkt_len, src_bytes, dst_bytes, payload = struct.unpack(dynamic_fmt,
                                                           byte_data)

    src = int.from_bytes(src_bytes,
                         byteorder=sys.byteorder,
                         signed=False)

    dst = int.from_bytes(dst_bytes,
                         byteorder=sys.byteorder,
                         signed=False)

    return np.NetPacket(src, dst, payload)


def is_valid_pkt(byte_data):
    '''
    Validates whether or not bytes represent a netpacket

    :param byte_data: Bytes to validate
    :returns: True if valid, False otherwise
    '''
    valid = False

    if len(byte_data) < (g_HEADER_SZ_BYTES + msgprotocol.g_HEADER_SZ_BYTES):
        # Pkt does not contains network header and message header
        valid = False
    else:
        # Check for valid message payload
        msg_payload = byte_data[g_HEADER_SZ_BYTES:]

        valid = msgprotocol.is_valid_msg(msg_payload)

    return valid


# Unit Testing
def test():
    enc_msg = '\x00\x12\x04message payload'.encode(
        c.Config.get(c.ConfigEnum.BYTE_ENCODING))
    pkt = np.NetPacket('173099348916645734434547360164674401582',
                       '173099348916645734434547360164674401583',
                       enc_msg)

    print('Pre-Serialization')
    print(pkt)

    enc_pkt = serialize(pkt)
    print('\nPost-Serialization')
    print(enc_pkt)

    # Check validation methods
    if not is_valid_pkt(enc_pkt):
        raise ValueError('Unable to validate packet during testing')

    dec_pkt = deserialize(enc_pkt)
    print('\nPost-Deserialization')
    print(dec_pkt)
