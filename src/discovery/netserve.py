"""
Module providing server for responding to Enpoint broadcasts over LAN.
Server runs on a separate thread from caller.
"""
import logging
from message import msg, msgprotocol
from network import netpacket, netprotocol
import select
import socket
import threading

_g_logger = logging.getLogger(__name__)


def kill():
    '''
    Gracefully stops the broadcast server and attempts to
    release thread resources.
    '''
    # Server is only killable if it has been started
    try:
        # 'start' called at least once but thread is inactive
        if not _g_mainloop_thread.is_alive():
            _g_logger.critical('Attempted to kill broadcast server'
                               ' which has not been started')

            raise RuntimeError('Cannot kill broadcast server'
                               ' which has not been started')
    except NameError:
        # 'start' never called so _g_mainloop_thread not defined
        _g_logger.critical('Attempted to kill broadcast server'
                           ' which has not been started')

        raise RuntimeError('Cannot kill broadcast server'
                           ' which has not been started')

    thread_join_timeout = 1.0  # Timeout (in sec.) for joining thread

    # Signal mainloop to exit
    _g_kill_sock.send(b'1')
    _g_kill_sock.close()

    _g_logger.info('Kill signal sent to broadcast server')

    # Attempt to join mainloop thread
    _g_mainloop_thread.join(timeout=thread_join_timeout)

    # Check if thread was joined in time
    if _g_mainloop_thread.is_alive():
        _g_logger.error('Unable to join broadcast server\'s thread')

    _g_logger.info('Broadcast server closed')


def __cleanup(inputs, outputs):
    '''
    Releases socket resources

    :param inputs: List of sockets to cleanup
    :param outputs: List of sockets to cleanup
    '''
    for s in inputs:
        s.close()

    for s in outputs:
        s.close()


def __mainloop(server, rx_port, host_ip, host_id, connection_map):
    '''
    Broadcast server's mainloop (should be run in separate thread)

    :param server: Server socket for detecting broadcasts
    :param rx_port: Port broadcast servers are listening over
    :param host_ip: IP address of local machine
    :param host_id: NetID for local machine used for response messages
    :param connection_map: Dict of connected endpoints - mapping {NetID: IP}
    '''
    _g_logger.info('Broadcast server\'s mainloop started')

    recv_buf_sz = 1024  # Max size of received data in bytes
    opt_val = 1         # For setting socket options
    done = False        # Flag indicating server mainloop should stop
    inputs = [server, _g_recv_kill_sock]    # Sockets to read
    outputs = []                            # Sockets to write
    msg_queues = {}     # Holds data to send with mapping {socket:(data,addr)}

    while inputs and not done:
        # Multiplex with 'select' call
        readable, writable, exceptional = select.select(inputs,
                                                        outputs,
                                                        inputs)
        # Readable sockets have data ready to read
        for s in readable:
            if s is server:
                # Potential broadcast received
                # rx_addr will be sending Endpoint's socket address
                rx_data, rx_addr = s.recvfrom(recv_buf_sz)
                _g_logger.info('Broadcast server received \'%s\' from \'%s\'',
                               rx_data, rx_addr)

                # Check if data available
                if not rx_data:
                    _g_logger.error('Received empty data')
                    continue  # No data read from socket

                # Deserialize packet
                try:
                    net_pkt = netprotocol.deserialize(rx_data)
                except ValueError:
                    _g_logger.error('Received data is not a valid packet')
                    continue  # Invalid packet

                # Sanity check IP addressing
                # Destination address in packet will be broadcast address
                if net_pkt.src != rx_addr[0] or net_pkt.src == host_ip:
                    _g_logger.error('Received data\'s addressing invalid')
                    continue  # Invalid address(es)

                # Determine the message type of the packet's payload
                pkt_msg = net_pkt.msg_payload
                msg_type = msgprotocol.decode_msgtype(pkt_msg)

                if msg_type is None:
                    _g_logger.error('Packet contained invalid payload')
                    continue  # Invalid message

                if msg_type == msg.MsgType.ENDPOINT_CONNECTION_RESPONSE:
                    # Received response from this Endpoint's
                    # connection broadcast
                    _g_logger.info('Broadcast response received')

                    # Extract information from message
                    net_id = msg.decode_payload(pkt_msg)

                    # Add device to connections list
                    connection_map[net_id] = net_pkt.src

                elif msg_type == msg.MsgType.ENDPOINT_CONNECTION_BROADCAST:
                    # Received an initial connection broadcast from
                    # another Endpoint
                    _g_logger.info('Connection broadcast received')

                    # Extract information from message
                    net_id = msg.decode_payload(pkt_msg)

                    # Spawn socket to send response and place into output list
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET,
                                    socket.SO_REUSEADDR,
                                    opt_val)

                    outputs.append(sock)

                    # Add socket with destination address to message queue
                    resp_addr = (rx_addr[0], rx_port)
                    msg_queues[sock] = resp_addr

                    # Add device to connections list
                    connection_map[net_id] = net_pkt.src

            elif s is _g_recv_kill_sock:
                _g_logger.info('Broadcast server received kill signal')

                done = True  # End server after this iteration of mainloop
                s.recv(recv_buf_sz)  # Clear out dummy data

        # Writable sockets have data ready to send
        for s in writable:
            # Get AF_INET address to send to from message queue
            dst_addr = msg_queues[s]

            # Construct response message
            resp_type = msg.MsgType.ENDPOINT_CONNECTION_RESPONSE
            broadcast_msg = msg.construct(resp_type, host_id)
            serialized_msg = msgprotocol.serialize(broadcast_msg)

            # Construct packet
            pkt = netpacket.NetPacket(host_ip, dst_addr[0], serialized_msg)
            serialized_pkt = netprotocol.serialize(pkt)

            # Send out data over socket
            s.sendto(serialized_pkt, dst_addr)

            _g_logger.info('Broadcast server sent \'%s\' to \'%s\'',
                           pkt, dst_addr)

            # Cleanup socket data
            s.close()
            outputs.remove(s)
            del msg_queues[s]

        # Exceptional sockets experience 'exceptional condition'
        for s in exceptional:
            # Raise exception if server is 'exceptional'
            # Unreleased resources will get garbage collected by OS
            if s is server:
                __cleanup(inputs, outputs)
                raise RuntimeError('Broadcast server encountered fatal error')

            # Remove from input/output channels if present
            try:
                inputs.remove(s)
            except ValueError:
                pass

            try:
                inputs.remove(s)
            except ValueError:
                pass

            # Delete message queue if present
            try:
                del msg_queues[s]
            except KeyError:
                pass

    # Cleanup sockets on exit
    __cleanup(inputs, outputs)


def start(rx_port, host_ip, host_id, connection_map):
    '''
    Starts up broadcast server's mainloop on separate thread
    and returns control to caller.

    :param rx_port: Port for broadcast server to listen on
    :param host_ip: IP address of local machine
    :param host_id: Endpoint NetID for local machine
    :param connection_map: Dict of connected endpoints - mapping {NetID: IP}
    '''
    global _g_kill_sock
    global _g_recv_kill_sock
    global _g_mainloop_thread

    opt_val = 1  # For setting socket options

    # Create/Configure TCP socket pair for returning control from 'select'
    _g_kill_sock, _g_recv_kill_sock = socket.socketpair(family=socket.AF_INET)

    _g_kill_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    _g_recv_kill_sock.setsockopt(socket.SOL_SOCKET,
                                 socket.SO_REUSEADDR,
                                 opt_val)

    _g_recv_kill_sock.setblocking(False)

    _g_logger.info('Dummy TCP socket pair created and configured')

    # Create and configure UDP server socket to receive UDP broadcasts
    server_addr = ('', rx_port)  # Listen on all interfaces

    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    server.setblocking(False)

    server.bind(server_addr)

    _g_logger.info('UDP broadcast server socket created and configured')

    # Startup server's mainloop and return control to caller
    _g_mainloop_thread = threading.Thread(target=__mainloop,
                                          args=(server,
                                                rx_port,
                                                host_ip,
                                                host_id,
                                                connection_map))
    _g_mainloop_thread.start()
