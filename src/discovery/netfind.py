"""
Module providing functionality for finding other Enpoints connected to the LAN
"""
from concurrent.futures import ThreadPoolExecutor
from message import msg, msgprotocol
from network import netpacket, netprotocol
from shared import utilities
import socket


def __broadcast(data, src_ip, dst_addr, connection_list):
    '''
    Sends out broadcast data to specified socket address

    :param data: Message to broadcast
    :param src_ip: IP of host
    :param dst_addr: Address of destination socket
    :param connection_list: Deque of connected endpoints - mapping (NetID, IP)
    '''
    opt_val = 1  # For setting socket options
    recv_buf_sz = 1024  # Max size of received data in bytes
    timeout = 2.0  # Timeout (in sec.) to wait for broadcast response

    # Construct netpacket
    serialized_msg = msgprotocol.serialize(data)
    pkt = netpacket.NetPacket(src_ip, dst_addr[0], serialized_msg)
    serialized_pkt = netprotocol.serialize(pkt)

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

        # Send out broadcast
        pkt_len = len(serialized_pkt)
        bytes_sent = 0

        while bytes_sent < pkt_len:
            bytes_sent += s.sendto(serialized_pkt[bytes_sent:], dst_addr)

        # Wait for response
        try:
            rx_data, rx_addr = s.recvfrom(recv_buf_sz)

            # Validate response and extract broadcast information
            valid = False

            if rx_data:
                # Check if data available
                valid = True

            if valid:
                # Check if data is a valid network packet
                try:
                    net_pkt = netprotocol.deserialize(rx_data)
                except ValueError:
                    # Discard invalid data
                    valid = False

            # Sanity check correct addressing
            if valid and (net_pkt.src != dst_addr[0] or net_pkt.dst != src_ip):
                valid = False

            # Check for correct msg type
            if valid \
               and msgprotocol.is_broadcast_response(net_pkt.msg_payload):
                # Extract data from message
                net_id = msg.decode_payload(net_pkt.msg_payload)
                connection = (net_id, net_pkt.dst)

                # Add device to connections list
                connection_list.append(connection)

        except socket.timeout:
            # No Endpoints detected
            pass


def execute(port, src_ip, net_id, connection_list):
    '''
    Executes message broadcasts to all valid network adapters. Blocks until
    all broadcasts have completed.

    :param port: Destination port to broadcast to
    :param src_ip: Host IP address
    :param net_id: Host's NetID
    :param connection_list: Deque of connected endpoints - mapping (NetID, IP)
    '''
    broadcast_ips = utilities.get_broadcast_ips()  # Check adapter info

    # Sanity check that network adapters are available for broadcasting
    num_broadcast_ips = len(broadcast_ips)
    if num_broadcast_ips == 0:
        raise RuntimeError('Unable to find valid network adapter')

    # Construct broadcasting message
    broadcast_msg = msg.construct(msg.MsgType.ENDPOINT_CONNECTION_BROADCAST,
                                  net_id)

    # Send out broadcasts and wait for replies
    with ThreadPoolExecutor(max_workers=num_broadcast_ips) as executor:
        for ip in broadcast_ips:
            executor.submit(__broadcast,
                            broadcast_msg,
                            src_ip,
                            (ip, port),
                            connection_list)
