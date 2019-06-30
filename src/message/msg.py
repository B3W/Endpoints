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


class ConnectionBroadcastMsg(Msg):
    """
    Derived class specifying format for connection broadcast message
    """

    def __init__(self, host_id):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_CONNECTION_BROADCAST)
        # TODO: SET PAYLOAD


class ConnectionResponseMsg(Msg):
    """
    Derived class specifying format for connection broadcast response message
    """

    def __init__(self, remote_id):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_CONNECTION_RESPONSE)
        # TODO: SET PAYLOAD


class DisconnectionBroadcastMsg(Msg):
    """
    Derived class specifying format for disconnection broadcast message
    """

    def __init__(self, host_id):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_DISCONNECTED_BROADCAST)
        # TODO: SET PAYLOAD


class CommunicationMsg(Msg):
    """
    Derived class specifying format for general message
    """

    def __init__(self, data):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_COMMUNICATION)
        # TODO: SET PAYLOAD


class AcknowledgementMsg(Msg):
    """
    Derived class specifying format for general message acknowledgement
    """

    def __init__(self):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_COMM_ACKNOWLEDGEMENT)
