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
        self.src = endpoint_src
        self.dst = endpoint_dst
        self.msg_payload = msg_payload

    def __len__(self):
        """
        Gets the length of NetPacket

        :returns: Length of packet encoded as bytes
        """
        return len(self.msg_payload)

    def __repr__(self):
        return '<%s src:%s dst:%s payload:%s>' \
            % (self.__class__.__name__, self.src.__repr__(),
               self.dst.__repr__(), self.msg_payload)

    def __str__(self):
        return '<\'%s\' Object Src:%s Dst:%s Payload:%s>' \
            % (self.__class__.__name__, self.src,
               self.dst, self.msg_payload)


# Unit Testing
def test():
    from network import netid

    src_id = netid.NetID('192.168.1.100')
    dst_id = netid.NetID('192.168.1.101')
    payload = 'this is a packet payload'.encode('utf-8')

    pkt = NetPacket(src_id, dst_id, payload)

    print('NetPacket __repr__')
    print(pkt.__repr__())

    print('\nNetPacket __str__')
    print(pkt)
