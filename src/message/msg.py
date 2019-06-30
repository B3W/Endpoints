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

    def __init__(self, msg_type, payload):
        """
        """
        self.msg_type = msg_type
        self.payload = payload

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
        super().__init__(MsgEnum.ENDPOINT_CONNECTION_BROADCAST,
                         host_id)


class ConnectionResponseMsg(Msg):
    """
    Derived class specifying format for connection broadcast response message
    """

    def __init__(self, remote_id):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_CONNECTION_RESPONSE,
                         remote_id)


class DisconnectionBroadcastMsg(Msg):
    """
    Derived class specifying format for disconnection broadcast message
    """

    def __init__(self, host_id):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_DISCONNECTED_BROADCAST,
                         host_id)


class CommunicationMsg(Msg):
    """
    Derived class specifying format for general message
    """

    def __init__(self, data):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_COMMUNICATION,
                         data)


class AcknowledgementMsg(Msg):
    """
    Derived class specifying format for general message acknowledgement
    """

    def __init__(self):
        """
        """
        super().__init__(MsgEnum.ENDPOINT_COMM_ACKNOWLEDGEMENT,
                         bytes())


@staticmethod
def construct(msg_type, payload):
    """
    Factory function for constructing a message of the appropriate
    type with the correct formatting for the payload

    :param msg_type: Enum representing message type
    :param payload: Raw message payload as Bytes

    :returns: Message object
    :raises: AttributeError if msg_type enum not supported
    """
    if msg_type == MsgEnum.ENDPOINT_COMMUNICATION:
        # TODO format payload
        return CommunicationMsg(payload)

    elif msg_type == MsgEnum.ENDPOINT_COMM_ACKNOWLEDGEMENT:
        return AcknowledgementMsg()

    elif msg_type == MsgEnum.ENDPOINT_CONNECTION_BROADCAST:
        # TODO format payload
        return ConnectionBroadcastMsg(payload)

    elif msg_type == MsgEnum.ENDPOINT_CONNECTION_RESPONSE:
        # TODO format payload
        return ConnectionResponseMsg(payload)

    elif msg_type == MsgEnum.ENDPOINT_DISCONNECTED_BROADCAST:
        # TODO format payload
        return DisconnectionBroadcastMsg(payload)

    else:
        raise AttributeError('%s message type not supported' % (msg_type.name))
