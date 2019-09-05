'''
Entry point for Enpoints application
'''
from collections import deque
from discovery import netserve, netfind
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
    # Get path to this module and construct configuration path
    main_path = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(main_path, 'config.json')

    # Load configuration
    c.Config.load(config_path)

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

    # Retrieve host's IP
    host_ip = utilities.get_host_ip()

    # Start UDP listener for connection broadcasts
    rx_port = c.Config.get(c.ConfigEnum.RX_PORT)
    # netserve.start(net_id, host_ip, rx_port)

    # Dict of connected and detected Endpoints with mapping (NetID, IP)
    endpoints = deque()

    # Find other endpoints on LAN
    netfind.execute(rx_port, host_ip, net_id, endpoints)

    print('Found following Endpoints on LAN:')
    for endpoint in endpoints:
        print(endpoint)

    # Testing
    # msg.test()
    # msgprotocol.test()
    # netid.test()
    # netpacket.test()
    # netprotocol.test()

    # Write configuration back to disk
    # c.Config.write()
