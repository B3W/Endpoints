'''
Module defining structure for Endpoint identifying information
'''


class NetID(object):
    '''
    Structure representing Endpoint identification
    '''

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
