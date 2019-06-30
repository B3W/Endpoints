"""
Module defining the protocol for sending and receiving
data between Endpoint applications.
"""
import struct


class MsgProtocol(object):
    """
    Class for serializing and deserializing data via
    length-prefixed message framing
    """

    NET_FMT = '!'   # Network(big-endian) byte ordering for packing/unpacking
    LEN_PREF_FMT = 'H'  # Length-prefix formatting
    MSG_TYPE_FMT = 'B'  # Message type flag formatting
    HEADER_FMT = NET_FMT + LEN_PREF_FMT + MSG_TYPE_FMT
    HEADER_SZ_BYTES = struct.calcsize(HEADER_FMT)

    def __init__(self):
        """
        MessageProtocol class initializer
        """
        # Format for variable message data
        self.var_data_fmt = '{}s'

        # Unpacking format for message header
        self.unpack_header_fmt = MsgProtocol.HEADER_FMT

        # Packing format with variable length data section
        self.pack_fmt = self.unpack_header_fmt + self.var_data_fmt

    def serialize(self, message):
        """
        Serializes message for sending over wire

        :param message: message to send

        :returns: Bytes object representing message to send
        """
        raise NotImplementedError('Class %s does not implement serialize()'
                                  % (self.__class__.__name__))

    def deserialize(self, byte_data):
        """
        Converts byte data into message object

        :param byte_data: bytes to convert to message

        :returns: Message object
        """
        raise NotImplementedError('Class %s does not implement deserialize()'
                                  % (self.__class__.__name__))
