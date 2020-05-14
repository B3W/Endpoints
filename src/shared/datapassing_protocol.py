'''
Module providing protocol for data passing between UI and background service
'''
import enum


@enum.unique
class DPMsgType(enum.Enum):
    '''Enum defining possible types of queue messages'''
    DPMSG_TYPE_CONNECTION = enum.auto()
    DPMSG_TYPE_TEXT_MSG = enum.auto()


@enum.unique
class DPMsgDst(enum.Enum):
    '''Enum defining possible destinations for a queue message'''
    DPMSG_DST_UI = enum.auto()
    DPMSG_DST_BACKEND = enum.auto()


class DPMsg(object):
    '''Base data passing message class'''
    def __init__(self, mtype, dst):
        '''
        :param mtype: Type of message
        :param dst: Destination of the message
        '''
        self.msg_type = mtype
        self.destination = dst


class DPTextMsg(DPMsg):
    '''Data passing message containing text to send or receive'''
    def __init__(self, dst, dst_id, timestamp, data):
        '''
        :param dst: Layer that message should be passed to
        :param dst_id: Endpoint's unique ID to send this message to
        '''
        super().__init__(DPMsgType.DPMSG_TYPE_TEXT_MSG, dst)
        self.destination_id = dst_id
        self.timestamp = timestamp
        self.data = data


class DPConnectionMsg(DPMsg):
    '''Data passing message indicating a new Endpoint connected'''
    def __init__(self, ep_id, ep_name):
        '''
        :param ep_id: Unique ID of Endpoint that connected
        '''
        super().__init__(DPMsgType.DPMSG_TYPE_CONNECTION,
                         DPMsgDst.DPMSG_DST_UI)
        self.endpoint_id = ep_id
        self.endpoint_name = ep_name
