'''
Module defining structure for Endpoint identifying information
'''
from shared import config as c
import struct


class NetID(object):
    '''
    Structure representing Endpoint identification
    '''
    GUID_SZ_BYTES = 16  # GUIDs are 128-bit integers
    GUID_PACK_FMT = f'{GUID_SZ_BYTES}s'  # GUID as bytes
    NAME_PACK_FMT = '%ds'  # Name string as bytes with dynamic length
    NETID_PACK_FMT = GUID_PACK_FMT + NAME_PACK_FMT  # Full format for packing

    def __init__(self, guid, name):
        '''
        NetID initialization

        :param guid: Endpoint GUID
        :param name: Endpoint friendly name
        '''
        self.guid = guid
        self.name = name
        # Add other ID as needed

    def __repr__(self):
        return '<%s id:%s name:%s>' \
            % (self.__class__.__name__, self.guid, self.name)

    def __str__(self):
        return '<\'%s\' Object ID:%s Name:%s>' \
            % (self.__class__.__name__, self.guid, self.name)


# Use struct.pack so identifications of various data types
# can be added to NetID in future
def tobytes(nid):
    '''
    :param nid: NetID object to be converted into bytes
    '''
    # Encode the NetID's friendly name and update pack format's length
    enc_name = nid.name.encode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))
    dynamic_fmt = NetID.NETID_PACK_FMT % (len(enc_name))

    return struct.pack(dynamic_fmt, nid.guid, enc_name)


# Use struct.pack so identifications of various data types
# can be added to NetID in future
def frombytes(nid):
    '''
    :param nid: Bytes representing a NetID object
    '''
    # Determine the length of the friendly string
    name_len = len(nid) - NetID.GUID_SZ_BYTES

    # Construct format then unpack bytes
    unpack_fmt = NetID.NETID_PACK_FMT % (name_len)
    guid, enc_name = struct.unpack(unpack_fmt, nid)

    # Construct and return a NetID object
    name = enc_name.decode(c.Config.get(c.ConfigEnum.BYTE_ENCODING))

    return NetID(guid, name)


# Unit Testing
def test():
    import copy

    nid = NetID('identification')

    # Test deepcopy functionality
    id_copy = copy.deepcopy(nid)
    id_copy.name = 'deepcopy\'s name'

    if nid == id_copy or nid.name == id_copy.name:
        print('NetID deepcopy creating shallow copy')

    # Test encoding functionality
    print('Pre-Encoding')
    print('%s\n' % (nid.__repr__()))

    enc = tobytes(nid)

    print('Post-Encoding')
    print('%s\n' % (enc))

    dec = frombytes(enc)

    print('Post-Decoding')
    print('%s\n' % (dec.__repr__()))
