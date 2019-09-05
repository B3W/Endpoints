"""
Module defining protocol for serializing and deserializing NetPackets for
sending and receiving data between Endpoint applications.
"""
from shared import config as c
from network import netpacket
import struct


_g_NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
_g_LEN_PREF_FMT = 'H'  # Length-prefix formatting (2 bytes alloted)
_g_SRC_IP_FMT = '15s'  # IP formatting (xxx.xxx.xxx.xxx)
_g_DST_IP_FMT = '15s'  # IP formatting (xxx.xxx.xxx.xxx)

# Bytes alloted for length prefix
g_LEN_PREF_SZ_BYTES = struct.calcsize(_g_LEN_PREF_FMT)

# Pkt 'header' format
g_MSG_HEADER_FMT = _g_NET_FMT + _g_LEN_PREF_FMT + _g_SRC_IP_FMT + _g_DST_IP_FMT
# Size of msg 'header'
g_HEADER_SZ_BYTES = struct.calcsize(g_MSG_HEADER_FMT)

variable_data_fmt = '%ds'  # Format for variable message data

# TODO: Add checksum onto end of packet

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

    return struct.pack(dynamic_fmt,
                       msg_sz,
                       packet.endpoint_src.encode(
                           c.Config.get(c.ConfigEnum.BYTE_ENCODING)),
                       packet.endpoint_dst.encode(
                           c.Config.get(c.ConfigEnum.BYTE_ENCODING)),
                       packet.msg_payload)


def deserialize(byte_data):
    """
    Converts byte data into NetPacket object

    :param byte_data: Bytes representing NetPacket

    :returns: NetPacket
    """
    payload_sz = len(byte_data) - g_HEADER_SZ_BYTES

    # Validate byte_data
    if payload_sz < 0:
        raise ValueError('Attempt to deserialize invalid packet')

    dynamic_fmt = unpack_fmt % (payload_sz)

    pkt_len, src, dst, payload = struct.unpack(dynamic_fmt, byte_data)

    # Decode IP addresses. IPs may have pad bytes if the address is not a full
    # 15 bytes during serialization (i.e. 192.168.100.100 vs 192.168.1.1).
    # Therefore, strip of all of those padding bytes after decoding.
    src = src.decode(c.Config.get(c.ConfigEnum.BYTE_ENCODING)).strip('\x00')
    dst = dst.decode(c.Config.get(c.ConfigEnum.BYTE_ENCODING)).strip('\x00')

    return netpacket.NetPacket(src, dst, payload)


# Unit Testing
def test():
    pkt = netpacket.NetPacket('127.0.0.1',
                              '127.0.0.2',
                              'message data'.encode(
                                  c.Config.get(c.ConfigEnum.BYTE_ENCODING)))

    print('Pre-Serialization')
    print(pkt)

    enc_pkt = serialize(pkt)
    print('\nPost-Serialization')
    print(enc_pkt)

    dec_pkt = deserialize(enc_pkt)
    print('\nPost-Deserialization')
    print(dec_pkt)
