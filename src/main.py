'''
Entry point for Enpoints application
'''
from collections import deque
from discovery import netserve, netfind
import logging
from network import netid
import os
import platform
from shared import config as c
from shared import utilities
# Testing
# from message import msg
# from message import msgprotocol
# from network import netid
# from network import netpacket
# from network import netprotocol

if __name__ == '__main__':
    # Get path to this module
    main_path = os.path.dirname(os.path.abspath(__file__))

    # Initialize logging module
    log_name = 'Endpoint-Log.log'
    log_path = os.path.join(main_path, '.logs', log_name)

    logging.basicConfig(filename=log_path, filemode='w',
                        format='%(asctime)s'
                               ' %(levelname)s(%(name)s): %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)

    # Retrieve logger
    logger = logging.getLogger(__name__)

    # Construct configuration path and load configuration
    config_path = os.path.join(main_path, 'config.json')
    c.Config.load(config_path)
    logger.info('Loaded configuration from %s', config_path)

    # Construct machine's NetID
    ep_name = c.Config.get(c.ConfigEnum.ENDPOINT_NAME).strip()

    if len(ep_name) == 0:
        # Use machine name if none specified in configuration
        # Try to get machine name via env vars, fallback to platform.node
        ep_name = os.getenv('HOSTNAME',
                            os.getenv('COMPUTERNAME', platform.node()))

        # Set value in config
        c.Config.set(c.ConfigEnum.ENDPOINT_NAME, ep_name)

    net_id = netid.NetID(ep_name)
    logger.debug('NetID: %s', net_id)

    # Retrieve host's IP
    host_ip = utilities.get_host_ip()
    logger.debug('Host IP: %s', host_ip)

    # Start UDP listener for connection broadcasts
    rx_port = c.Config.get(c.ConfigEnum.RX_PORT)
    logger.debug('RX Port: %d', rx_port)

    netserve.start(rx_port, host_ip, net_id)
    logger.info('Broadcast server started')

    # Dict of connected and detected Endpoints with mapping (NetID, IP)
    endpoints = deque()

    # Find other endpoints on LAN
    netfind.execute(rx_port, host_ip, net_id, endpoints)
    logger.info('Detection of other Endpoints complete')
    logger.debug('Endpoints: %s', endpoints)

    # FOR TESTING PURPOSES ONLY
    import signal
    from time import sleep

    def sigint_handler(signum, stack_frame):
        global done
        netserve.kill()
        done = True

    signal.signal(signal.SIGINT, sigint_handler)

    global done
    done = False

    while not done:
        sleep(1.0)

    signal.signal(signal.SIGINT, signal.default_int_handler)

    # Testing
    # msg.test()
    # msgprotocol.test()
    # netid.test()
    # netpacket.test()
    # netprotocol.test()

    # Write configuration back to disk
    # c.Config.write()
