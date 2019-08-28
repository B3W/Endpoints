'''
Module defining structure for Endpoint identifying information
'''
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
        return self.endpoint_name.encode('utf-8')

    def __len__(self):
        return len(self.tobytes())

    def __repr__(self):
        return '<%s name:%s>' \
            % (self.__class__.__name__, self.endpoint_name)


def frombytes(id):
    unpack_fmt = NetID.NAME_FMT % (len(id))
    name = struct.unpack(unpack_fmt, id)

    return NetID(name)
