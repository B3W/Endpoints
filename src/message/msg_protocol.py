"""
Module defining the protocol for sending and receiving
data between Endpoint applications.
"""
import msg
import struct


class MsgProtocol(object):
    """
    Class for serializing and deserializing data via
    length-prefixed message framing
    """

    NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
    LEN_PREF_FMT = 'H'  # Length-prefix formatting
    MSG_TYPE_FMT = 'B'  # Msg type flag formatting
    HEADER_FMT = NET_FMT + LEN_PREF_FMT + MSG_TYPE_FMT  # Msg 'header' format

    LEN_PREF_SZ_BYTES \
        = struct.calcsize(LEN_PREF_FMT)  # Bytes alloted for length prefix
    HEADER_SZ_BYTES   \
        = struct.calcsize(HEADER_FMT)    # Size of msg 'header'

    def __init__(self):
        """
        MessageProtocol class initializer
        """
        # Format for variable message data
        self.var_data_fmt = '%ds'

        # Struct format for message header
        self.header_fmt = MsgProtocol.HEADER_FMT

        self.unpack_fmt = MsgProtocol.NET_FMT   \
            + MsgProtocol.MSG_TYPE_FMT      \
            + self.var_data_fmt

        # Packing format with variable length data section
        self.pack_fmt = self.header_fmt + self.var_data_fmt

    def serialize(self, message):
        """
        Serializes message for sending over wire

        :param message: message to send

        :returns: Bytes object representing message to send
        """
        dynamic_fmt = self.pack_fmt % (len(message))
        msg_sz = struct.calcsize(dynamic_fmt)

        return struct.pack(dynamic_fmt,
                           msg_sz,
                           message.msg_type,
                           message.payload)

    def deserialize(self, byte_data, byte_len):
        """
        Converts byte data into message object

        :param byte_data: bytes to convert to message
        :param byte_len: length of byte data

        :returns: Message object
        """
        dynamic_fmt = self.unpack_fmt % (byte_len - 1)

        msg_type, payload = struct.unpack(dynamic_fmt, byte_data)

        return msg.construct(msg_type, payload)
