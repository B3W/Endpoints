'''
Module providing protocol for data passing between UI and background service
'''
import enum
import struct

# Type,SenderID,ISOTimestamp,DataLen,Data
NET_FMT = '!'
TYPE_FMT = 'H'  # Type of queue message
TYPE_LEN_BYTES = struct.calcsize(TYPE_FMT)
ID_FMT = '16s'
TIMESTAMP_FMT = '16s'

TEXT_HEADER_FMT = NET_FMT + TYPE_FMT + ID_FMT + TIMESTAMP_FMT
TEXT_HEADER_LEN_BYTES = struct.calcsize(TEXT_HEADER_FMT)
CONN_HEADER_FMT = NET_FMT + TYPE_FMT + ID_FMT
CONN_HEADER_LEN_BYTES = struct.calcsize(CONN_HEADER_FMT)
variable_fmt = '%ds'


@enum.unique
class QDataType(enum.Enum):
    CONNECTION = enum.auto()
    TEXT_MSG = enum.auto()


def decode_qdata_type(byte_data):
    raw_qdata_type = byte_data[:TYPE_LEN_BYTES]
    qdata_type = struct.unpack(NET_FMT + TYPE_FMT, raw_qdata_type)

    return qdata_type


def text_encode(ident, timestamp, data):
    '''
    :param ident: bytes obj representing Endpoint's unique ID
    '''
    encoded_ts = timestamp.encode()
    encoded_data = data.encode()

    data_len = len(encoded_data)
    data_fmt = variable_fmt % data_len

    pack_fmt = TEXT_HEADER_FMT + data_fmt

    return struct.pack(pack_fmt,
                       QDataType.TEXT_MSG,
                       ident,
                       encoded_ts,
                       encoded_data)


def text_decode(byte_data):
    '''
    '''
    header = byte_data[:TEXT_HEADER_LEN_BYTES]
    data_type, ident, raw_ts = struct.unpack(TEXT_HEADER_FMT, header)

    raw_data = byte_data[TEXT_HEADER_LEN_BYTES:]

    return ident, raw_ts.decode(), raw_data.decode()


def conn_encode(ident, name):
    '''
    :param ident: bytes obj representing Endpoint's unique ID
    '''
    encoded_name = name.encode()
    name_len = len(encoded_name)

    pack_fmt = CONN_HEADER_FMT + (variable_fmt % name_len)

    return struct.pack(pack_fmt,
                       QDataType.CONNECTION,
                       ident,
                       encoded_name)


def conn_decode(byte_data):
    '''
    '''
    data_type, ident = byte_data[:CONN_HEADER_LEN_BYTES]
    raw_name = byte_data[CONN_HEADER_LEN_BYTES:]

    return ident, raw_name.decode()
