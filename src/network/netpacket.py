"""
Module defining Enpoint network packet structure.
"""


class NetPacket(object):
    """
    Structure for sending data between Endpoints
    """

    def __init__(self, endpoint_src, endpoint_dst, msg_payload):
        """
        'Constructor' for NetPacket

        :param endpoint_src: Source node IP
        :param endpoint_dst: Destination node IP
        :param msg_payload: Encoded message to send
        """
        self.endpoint_src = endpoint_src
        self.endpoint_dst = endpoint_dst
        self.msg_payload = msg_payload

    def __len__(self):
        """
        Gets the length of NetPacket

        :returns: Length of packet encoded as bytes
        """
        return len(self.msg_payload)

    def __repr__(self):
        return '<%s src:%s dst:%s payload:%s>' \
            % (self.__class__.__name__, self.endpoint_src.__repr__(),
               self.endpoint_dst.__repr__(), self.msg_payload)

    def __str__(self):
        return '\'%s\' Object\nSrc:%s\nDst:%s\nPayload:%s' \
            % (self.__class__.__name__, self.endpoint_src,
               self.endpoint_dst, self.msg_payload)


# Unit Testing
if __name__ == '__main__':
    import netid

    src_id = netid.NetID('endpoint1', '192.168.100.1')
    dst_id = netid.NetID('endpoint2', '192.168.100.2')
    payload = 'this is a packet payload'.encode('utf-8')

    pkt = NetPacket(src_id, dst_id, payload)

    print('NetPacket __repr__')
    print(pkt.__repr__())

    print('\nNetPacket __str__')
    print(pkt)
