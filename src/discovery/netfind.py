"""
Module providing functionality for broadcasting connection messages over the
available network interfaces.
"""
from concurrent.futures import ThreadPoolExecutor
import logging
from message import msg, msgprotocol
from network import netpacket, netprotocol
from shared import utilities
import socket

_g_logger = logging.getLogger(__name__)


def __broadcast(data, src_ip, dst_addr):
    '''
    Sends out broadcast data to specified socket address

    :param data: Message to broadcast
    :param src_ip: IP of host
    :param dst_addr: Address of destination socket
    '''
    opt_val = 1  # For setting socket options

    # Construct netpacket
    serialized_msg = msgprotocol.serialize(data)
    pkt = netpacket.NetPacket(src_ip, dst_addr[0], serialized_msg)
    serialized_pkt = netprotocol.serialize(pkt)

    _g_logger.debug('Constructed broadcasting packet: %s', serialized_pkt)

    # Create/Configure UDP socket for broadcasting
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Socket reuse
        s.setsockopt(socket.SOL_SOCKET,
                     socket.SO_REUSEADDR,
                     opt_val)
        # Enable broadcasting on socket
        s.setsockopt(socket.SOL_SOCKET,
                     socket.SO_BROADCAST,
                     opt_val)

        _g_logger.info('Socket for broadcasting created and configured')

        # Send out broadcast
        pkt_len = len(serialized_pkt)
        bytes_sent = 0

        while bytes_sent < pkt_len:
            bytes_sent += s.sendto(serialized_pkt[bytes_sent:], dst_addr)

        _g_logger.info('Broadcast sent')


def execute(port, src_ip, net_id):
    '''
    Executes message broadcasts to all valid network adapters. Blocks until
    all broadcasts have been sent out.

    :param port: Destination port to broadcast to
    :param src_ip: Host IP address
    :param net_id: Host's NetID
    '''
    broadcast_ips = utilities.get_broadcast_ips()  # Check adapter info
    _g_logger.debug('Broadcast IPs: %s', broadcast_ips)

    # Sanity check that network adapters are available for broadcasting
    num_broadcast_ips = len(broadcast_ips)
    if num_broadcast_ips == 0:
        raise RuntimeError('Unable to find valid network adapter')

    _g_logger.info('Broadcasting IPs retrieved')

    # Construct broadcasting message
    broadcast_msg = msg.construct(msg.MsgType.ENDPOINT_CONNECTION_BROADCAST,
                                  net_id)
    _g_logger.debug('Constructed broadcast message: %s', broadcast_msg)

    # Send out broadcasts
    with ThreadPoolExecutor(max_workers=num_broadcast_ips) as executor:
        for ip in broadcast_ips:
            executor.submit(__broadcast, broadcast_msg, src_ip, (ip, port))
