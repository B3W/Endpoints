"""
Module defining protocol for serializing and deserializing NetPackets for
sending and receiving data between Endpoint applications.
"""
from network import netpacket
import struct


NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
LEN_PREF_FMT = 'H'  # Length-prefix formatting (2 bytes alloted)
SRC_IP_FMT = '15s'  # IP formatting (xxx.xxx.xxx.xxx)
DST_IP_FMT = '15s'  # IP formatting (xxx.xxx.xxx.xxx)
MSG_HEADER_FMT = NET_FMT + LEN_PREF_FMT \
    + SRC_IP_FMT + DST_IP_FMT  # Pkt 'header' format

variable_data_fmt = '%ds'  # Format for variable message data

# TODO: Add checksum onto end of packet

LEN_PREF_SZ_BYTES \
    = struct.calcsize(LEN_PREF_FMT)  # Bytes alloted for length prefix
HEADER_SZ_BYTES   \
    = struct.calcsize(MSG_HEADER_FMT)    # Size of msg 'header'

pack_fmt = MSG_HEADER_FMT + variable_data_fmt  # Packing format
unpack_fmt = MSG_HEADER_FMT + variable_data_fmt  # Unpacking format


def serialize(packet):
    """
    Serializes packet for sending over wire

    :param packet: NetPacket to serialize

    :returns: Bytes object representing NetPacket to send
    """
    dynamic_fmt = pack_fmt % (len(packet))
    msg_sz = struct.calcsize(dynamic_fmt)

    return struct.pack(dynamic_fmt,
                       msg_sz,
                       packet.endpoint_src.encode('utf-8'),
                       packet.endpoint_dst.encode('utf-8'),
                       packet.msg_payload)


def deserialize(byte_data):
    """
    Converts byte data into NetPacket object

    :param byte_data: Bytes representing NetPacket

    :returns: NetPacket
    """
    payload_sz = len(byte_data) - HEADER_SZ_BYTES
    dynamic_fmt = unpack_fmt % (payload_sz)

    pkt_len, src, dst, payload = struct.unpack(dynamic_fmt, byte_data)

    return netpacket.NetPacket(src.decode('utf-8'),
                               dst.decode('utf-8'),
                               payload)


# Unit Testing
def test():
    pkt = netpacket.NetPacket('127.000.000.001',
                              '127.000.000.002',
                              'message data'.encode('utf-8'))

    print('Pre-Serialization')
    print(pkt)

    enc_pkt = serialize(pkt)
    print('\nPost-Serialization')
    print(enc_pkt)

    dec_pkt = deserialize(enc_pkt)
    print('\nPost-Deserialization')
    print(dec_pkt)
