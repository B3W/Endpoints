"""
Module defining message data formats.
"""
from msg_enum import MsgEnum


class Msg(object):
    """
    Base class for message data formats.
    Derived classes specify different data formats for messages
    sent between Endpoint applications.
    """

    def __init__(self, msg_type):
        """
        """
        self.payload = bytes()
        self.msg_type = msg_type

    def __len__(self):
        """
        Gets the length of the message

        :returns: Length of message payload
        """
        return len(self.payload)


class DiscoverPollMsg(Msg):
    """
    Derived class specifying format for discovery message poll
    """

    def __init__(self, host_ip, host_port):
        """
        """
        super().__init__(MsgEnum.DISCOVERY_POLL)
        # TODO: SET PAYLOAD


class DiscoverRespMsg(Msg):
    """
    Derived class specifying format for discovery message response
    """

    def __init__(self, remote_ip, remote_port):
        """
        """
        super().__init__(MsgEnum.DISCOVERY_RESP)
        # TODO: SET PAYLOAD


class CommunicationMsg(Msg):
    """
    Derived class specifying format for general message
    """

    def __init__(self, data):
        """
        """
        super().__init__(MsgEnum.COMMUNICATION)
        # TODO: SET PAYLOAD


class AcknowledgementMsg(Msg):
    """
    Derived class specifying format for general message acknowledgement
    """

    def __init__(self):
        """
        """
        super().__init__(MsgEnum.ACK)
