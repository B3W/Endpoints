"""
Module providing functionality for finding other Enpoints connected to the LAN
"""
from concurrent.futures import ThreadPoolExecutor
import logging
from message import msg, msgprotocol
from network import netpacket, netprotocol
from shared import utilities
import socket

_g_logger = logging.getLogger(__name__)


def __broadcast(data, src_ip, dst_addr, connection_map):
    '''
    Sends out broadcast data to specified socket address

    :param data: Message to broadcast
    :param src_ip: IP of host
    :param dst_addr: Address of destination socket
    :param connection_map: Dict of connected endpoints - mapping {NetID: IP}
    '''
    opt_val = 1  # For setting socket options
    recv_buf_sz = 1024  # Max size of received data in bytes
    timeout = 2.0  # Timeout (in sec.) to wait for broadcast response

    # Construct netpacket
    serialized_msg = msgprotocol.serialize(data)
    pkt = netpacket.NetPacket(src_ip, dst_addr[0], serialized_msg)
    serialized_pkt = netprotocol.serialize(pkt)

    _g_logger.debug('Constructed NetPacket: %s', serialized_pkt)

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

        s.settimeout(timeout)

        _g_logger.info('Socket created and configured')

        # Send out broadcast
        pkt_len = len(serialized_pkt)
        bytes_sent = 0

        while bytes_sent < pkt_len:
            bytes_sent += s.sendto(serialized_pkt[bytes_sent:], dst_addr)

        _g_logger.info('Broadcast sent')

        # Wait for response
        try:
            rx_data, rx_addr = s.recvfrom(recv_buf_sz)

            _g_logger.info('Broadcast response received')
            _g_logger.debug('Addr: %s; Data: %s', rx_addr, rx_data)

            # Validate response and extract broadcast information
            valid = False

            if rx_data:
                # Check if data available
                valid = True
                _g_logger.error('Received empty data')

            if valid:
                # Check if data is a valid network packet
                try:
                    net_pkt = netprotocol.deserialize(rx_data)
                except ValueError:
                    # Discard invalid data
                    valid = False
                    _g_logger.error('Received data is not a valid packet')

            # Sanity check correct addressing
            if valid and (dst_addr[0] != rx_addr[0]
               or net_pkt.src != dst_addr[0]
               or net_pkt.dst != src_ip):
                valid = False
                _g_logger.error('Received data\'s addressing invalid')

            # Check for correct msg type
            if valid \
               and msgprotocol.is_broadcast_response(net_pkt.msg_payload):
                _g_logger.info('Valid broadcast response received')

                # Extract data from message
                net_id = msg.decode_payload(net_pkt.msg_payload)

                _g_logger.debug('Extracted NetID from broadcast response: %s',
                                net_id)

                # Add device to connections list
                connection_map[net_id] = net_pkt.src

                _g_logger.info('Device appended to connection list')

        except socket.timeout:
            # No Endpoints detected
            _g_logger.info('No response received from broadcast: %s',
                           dst_addr[0])


def execute(port, src_ip, net_id, connection_map):
    '''
    Executes message broadcasts to all valid network adapters. Blocks until
    all broadcasts have completed.

    :param port: Destination port to broadcast to
    :param src_ip: Host IP address
    :param net_id: Host's NetID
    :param connection_map: Dict of connected endpoints - mapping {NetID: IP}
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

    # Send out broadcasts and wait for replies
    with ThreadPoolExecutor(max_workers=num_broadcast_ips) as executor:
        for ip in broadcast_ips:
            executor.submit(__broadcast,
                            broadcast_msg,
                            src_ip,
                            (ip, port),
                            connection_map)
