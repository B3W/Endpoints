'''
Module providing protocol for data passing between UI and background service
'''
import enum


@enum.unique
class QDataType(enum.Enum):
    CONNECTION = enum.auto()
    TEXT_MSG = enum.auto()


class TextMsg(object):
    def __init__(self, ident, timestamp, data):
        '''
        :param ident: bytes obj representing Endpoint's unique ID
        '''
        self.type = QDataType.TEXT_MSG
        self.ident = ident
        self.timestamp = timestamp
        self.data = data


class Connection(object):
    def __init__(self, ident, name):
        '''
        :param ident: bytes obj representing Endpoint's unique ID
        '''
        self.type = QDataType.CONNECTION
        self.ident = ident
        self.name = name
