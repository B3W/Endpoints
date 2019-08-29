'''
Module defining structure for Endpoint identifying information
'''
from config import config as c
import struct


class NetID(object):
    '''
    Structure representing Endpoint identification
    '''
    NAME_FMT = '%ds'

    def __init__(self, name):
        '''
        NetID initialization

        :param name: Endpoint name
        '''
        self.endpoint_name = name
        # Add other ID as needed

    def tobytes(self):
        # Use struct.pack so identifications of various data types
        # can be added to NetID in future
        enc_name = self.endpoint_name.encode(
            c.Config.get(c.ConfigEnum.BYTE_ENCODING))

        pack_fmt = NetID.NAME_FMT % (len(enc_name))

        return struct.pack(pack_fmt, enc_name)

    def __len__(self):
        return len(self.tobytes())

    def __repr__(self):
        return '<%s name:%s>' \
            % (self.__class__.__name__, self.endpoint_name)


def frombytes(id):
    # Use struct.unpack so identifications of various data types
    # can be added to NetID in future
    unpack_fmt = NetID.NAME_FMT % (len(id))

    enc_name, = struct.unpack(unpack_fmt, id)

    name = enc_name.decode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))

    return NetID(name)


# Unit Testing
def test():
    id = NetID('identification')

    print('Pre-Encoding')
    print('%s\n' % (id.__repr__()))

    enc = id.tobytes()

    print('Post-Encoding')
    print('%s\n' % (enc))

    dec = frombytes(enc)

    print('Post-Decoding')
    print('%s\n' % (dec.__repr__()))
