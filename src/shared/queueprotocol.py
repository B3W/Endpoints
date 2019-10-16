'''
Module providing protocol for data passing between UI and background service
'''
import struct

# SenderID,ISOTimestamp,DataLen,Data
ID_FMT = '16s'
TIMESTAMP_FMT = '16s'
variable_fmt = '%ds'
HEADER_FMT = ID_FMT + TIMESTAMP_FMT
HEADER_LEN_BYTES = struct.calcsize(HEADER_FMT)


def encode(ident, timestamp, data):
    '''
    Packs data to be placed into data passing queue

    :param ident: bytes obj representing Endpoint's unique ID
    :param timestamp: string representing data's timestamp
    '''
    encoded_ts = timestamp.encode()
    encoded_data = data.encode()

    data_len = len(encoded_data)
    data_fmt = variable_fmt % data_len

    pack_fmt = HEADER_FMT + data_fmt

    return struct.pack(pack_fmt, ident, encoded_ts, encoded_data)


def decode(byte_data):
    '''
    Decodes data from data passing queue

    :param byte_data: Data to decode
    '''
    header = byte_data[:HEADER_LEN_BYTES]
    ident, raw_ts = struct.unpack(HEADER_FMT, header)

    raw_data = byte_data[HEADER_LEN_BYTES:]

    return ident, raw_ts.decode(), raw_data.decode()
