"""
Module providing server for responding to Enpoint broadcasts over LAN.
Server runs on a separate thread from caller.
"""
import logging
from message import msg, msgprotocol
from network import netprotocol
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


def __cleanup(sockets):
    '''
    Releases socket resources

    :param sockets: List of sockets to cleanup
    '''
    for s in socket:
        s.close()


def __buffer_data(data_buffer, rx_addr, rx_data):
    '''
    Buffer data and check if a full message was received

    :returns: True if a full message was received, False otherwise
    '''
    full_message = False
    rx_data_len = len(rx_data)

    # Buffer data
    try:
        data_buffer[rx_addr] += rx_data
    except KeyError:
        data_buffer[rx_addr] = rx_data

    # Extract packet's length field and compare
    len_field = data_buffer[rx_addr][:netprotocol.g_LEN_PREF_SZ_BYTES]
    pkt_len = socket.ntohs(len_field)

    if rx_data_len == pkt_len:
        full_message = True
    elif rx_data_len < pkt_len:
        full_message = False
    else:
        del data_buffer[rx_addr]
        _g_logger.error('Received packet was too long...')
        _g_logger.error('Expected Length: %d; Actual Length: %d',
                        pkt_len, rx_data_len)

    return full_message


def __clear_buffer(data_buffer, rx_addr):
    '''
    Delete buffered data for specified IP if it exists
    '''
    try:
        del data_buffer[rx_addr]
    except KeyError:
        pass


def __validate_broadcast(rx_data, host_guid):
    '''
    '''
    valid = True
    net_pkt = None

    # Check if data available
    if not rx_data:
        valid = False
        _g_logger.error('Received empty data')

    # Deserialize packet
    if valid:
        try:
            net_pkt = netprotocol.deserialize(rx_data)
        except ValueError:
            valid = False
            _g_logger.error('Received data is not a valid packet: %s'
                            % rx_data)

    # Sanity check sender's GUID
    if valid:
        if net_pkt.src == host_guid:
            valid = False
            _g_logger.error('Broadcast received from self: %s'
                            % net_pkt)

    return net_pkt, valid


def __mainloop(server, cast_port, host_guid, request_queue):
    '''
    Broadcast server's mainloop (should be run in separate thread)

    :param server: Server socket for detecting broadcasts
    :param cast_port: Port broadcast servers are listening over
    :param host_guid: GUID of local machine
    :param request_queue: Queue for writing new connection requests into
    '''
    _g_logger.info('Broadcast server\'s mainloop started')

    recv_buf_sz = 1024  # Max size of received data in bytes
    done = False        # Flag indicating server mainloop should stop
    inputs = [server, _g_recv_kill_sock]    # Sockets to read
    data_buffer = {}  # Keeps track of received data {IP: data}

    while inputs and not done:
        # Multiplex with 'select' call
        readable, _, exceptional = select.select(inputs, [], inputs)

        # Readable sockets have data ready to read
        for s in readable:
            if s is server:
                # Potential broadcast received
                # 'rx_addr' is sending Endpoint's socket address
                rx_data, rx_addr = s.recvfrom(recv_buf_sz)
                _g_logger.info('Broadcast server received \'%s\' from \'%s\'',
                               rx_data, rx_addr)

                # Check if the full message was received
                full_message = __buffer_data(data_buffer, rx_addr, rx_data)

                if not full_message:
                    continue

                # Validate
                net_pkt, valid = __validate_broadcast(data_buffer[rx_addr],
                                                      host_guid)

                if not valid:
                    __clear_buffer(data_buffer, rx_addr)
                    continue

                # Determine the message type of the packet's payload
                pkt_msg = net_pkt.msg_payload
                msg_type = msgprotocol.decode_msgtype(pkt_msg)

                if msg_type == msg.MsgType.ENDPOINT_CONNECTION_BROADCAST:
                    # Received connection broadcast from another Endpoint
                    _g_logger.info('Connection broadcast received')

                    # Extract information from message
                    net_id = msg.decode_payload(pkt_msg)

                    # Report device connection request
                    device = (net_pkt.src, rx_addr, net_id.name)
                    request_queue.put(device)

                    __clear_buffer(data_buffer, rx_addr)

                else:
                    _g_logger.error('Invalid broadcast payload type: %s'
                                    % msg_type)

            elif s is _g_recv_kill_sock:
                _g_logger.info('Broadcast server received kill signal')
                s.recv(recv_buf_sz)  # Clear out dummy data
                done = True  # End server after this iteration of mainloop

            else:
                s.close()
                _g_logger.error('Invalid \'readable\' socket')

        # Exceptional sockets experience 'exceptional condition'
        for s in exceptional:
            # Raise exception if server is 'exceptional'
            # Unreleased resources will get garbage collected by OS
            __cleanup(inputs)

            if s is server:
                _g_logger.critical('Broadcast server encountered fatal error')
                raise RuntimeError('Broadcast server encountered fatal error')

            else:
                _g_logger.critical('Non-server socket encountered fatal error')
                raise RuntimeError('Non-server socket encountered fatal error')

    # Cleanup sockets on exit
    __cleanup(inputs)
    _g_logger.info('Broadcast server closed')


def start(cast_port, host_guid, request_queue):
    '''
    Starts up broadcast server's mainloop on separate thread
    and returns control to caller.

    :param cast_port: Port for broadcast server to listen on
    :param host_guid: GUID of local machine
    :param request_queue: Queue for writing new connection requests into
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
    server_addr = ('', cast_port)  # Listen on all interfaces

    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    server.setblocking(False)

    server.bind(server_addr)
    _g_logger.info('UDP broadcast server socket created and configured')

    # Startup server's mainloop and return control to caller
    _g_mainloop_thread = threading.Thread(target=__mainloop,
                                          args=(server,
                                                cast_port,
                                                host_guid,
                                                request_queue))
    _g_mainloop_thread.start()
