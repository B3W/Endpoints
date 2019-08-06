"""
Module defining Enpoint network identification structure.
"""


class NetID(object):
    """
    NetID class.
    """

    def __init__(self, endpoint_name, endpoint_ip):
        """
        'Constructor' for NetID

        :param endpoint_name: Friendly name for the Endpoint
        :param endpoint_ip: IP address of the Endpoint
        """
        self.endpoint_name = endpoint_name
        self.endpoint_ip = endpoint_ip
        # Add other identifications as needed

    def __len__(self):
        """
        Gets the length of NetID

        :returns: Length of byte representation of NetID object
        """
        return len(self.endpoint_name.encode('utf-8')
                   + self.endpoint_ip.encode('utf-8'))

    def __repr__(self):
        return '<%s name:%s ip:%s>' \
            % (self.__class__.__name__, self.endpoint_name, self.endpoint_ip)

    def __str__(self):
        return '\'%s\' Object\nName:%s\nIP:%s' \
            % (self.__class__.__name__, self.endpoint_name, self.endpoint_ip)
