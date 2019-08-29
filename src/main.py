'''
Entry point for Enpoints application
'''
from config import config
# Testing
# from message import msg
# from message import msgprotocol
# from network import netpacket
# from network import netprotocol

if __name__ == '__main__':
    # Load configuration
    config.Config.load()

    # Testing
    # msg.test()
    # msgprotocol.test()
    # netpacket.test()
    # netprotocol.test()

    # Write configuration back to disk
    # config.Config.write()
