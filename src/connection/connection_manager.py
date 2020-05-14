"""
Module providing server listening for Enpoint conversation connections.
Server runs on a separate thread from caller.
"""
import datapassing
from shared import datapassing_protocol as dp_proto
import logging
from message import msg, msgprotocol
from network import netprotocol
import select
import socket
import threading

_g_logger = logging.getLogger(__name__)


def send_msg():
    ''''''
    # TODO Construct network message
    # TODO Queue message to be sent over appropriate socket
    pass


def __notify_ui_of_connection(net_id):
    '''Passes connection information to UI'''
    # Report connection to the UI
    ui_message = dp_proto.DPConnectionMsg(net_id.guid, net_id.name)
    datapassing.pass_msg(ui_message)


def __notify_ui_of_text_data(guid, timestamp, data):
    '''Passes text data to UI'''
    # Report text data to UI
    ui_message = dp_proto.DPTextMsg(dp_proto.DPMsgDst.DPMSG_DST_UI,
                                    guid,
                                    timestamp,
                                    data)
    datapassing.pass_msg(ui_message)


def __cleanup(sockets):
    '''
    Releases socket resources

    :param sockets: List of sockets to cleanup
    '''
    for s in socket:
        s.close()


def __validate_pkt(rx_data, host_guid):
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
            _g_logger.error(f'Received data is not a valid packet: {rx_data}')

    # Sanity check sender's GUID
    if valid:
        if net_pkt.src == host_guid:
            valid = False
            _g_logger.error(f'Connection received from self: {net_pkt}')

    return net_pkt, valid


def __process_rx_data(addr, data, sock, host_guid):
    '''
    '''
    global _g_inputs
    global _g_connection_map

    if data:
        # Make sure received data is a valid packet
        net_pkt, valid = __validate_pkt(data, host_guid)

        if not valid:
            _g_inputs.remove(sock)
            sock.close()
            _g_logger.error("Received invalid packet")
            return

        # Extract message type of the packet's payload
        msg_type = msgprotocol.decode_msgtype(net_pkt.msg_payload)

        if msg_type == msg.MsgType.ENDPOINT_CONNECTION_START:
            # A connection was accepted
            _g_logger.info("Connection accepted")

            message = msgprotocol.deserialize(net_pkt.msg_payload)
            net_id = msg.decode_payload(message)

            if net_id.guid not in _g_connection_map:
                __notify_ui_of_connection(net_id)

            # Record/Update active connection {GUID: (name, socket)}
            _g_connection_map[net_id.guid] = (net_id.name, sock)

        elif msg_type == msg.MsgType.ENDPOINT_TEXT_COMMUNICATION:
            # A connection sent text data
            _g_logger.info("Text data received")

            message = msgprotocol.deserialize(net_pkt.msg_payload)
            text_data = msg.decode_payload(message)

            __notify_ui_of_text_data(net_pkt.src, message.timestamp, text_data)
            pass

        elif msg_type == msg.MsgType.ENDPOINT_DISCONNECTION:
            # A connection is getting disconnected
            _g_logger.info("Disconnection reported")

            message = msgprotocol.deserialize(net_pkt.msg_payload)
            net_id = msg.decode_payload(message)

            # TODO Report disconnection to UI

            # Close the connection
            _g_inputs.remove(sock)
            sock.close()
            del _g_connection_map[net_id.guid]

        else:
            _g_logger.error('Invalid connection payload type: %s'
                            % msg_type)

    else:
        # Something went wrong
        _g_inputs.remove(sock)
        sock.close()


def __mainloop(server, host_guid):
    '''
    Connection server's mainloop (should be run in separate thread)

    :param server: Server socket for detecting connections
    :param host_guid: GUID of local machine
    '''
    _g_logger.info('Connection server\'s mainloop started')

    global _g_inputs
    global _g_outputs

    RECV_BUF_SZ = 1024  # Max size of received data in bytes
    done = False        # Flag indicating server mainloop should stop
    _g_inputs = [server, _g_recv_kill_sock]    # Sockets to read
    _g_outputs = []

    while _g_inputs and not done:
        # Multiplex with 'select' call
        readable, writable, exceptional = select.select(_g_inputs,
                                                        _g_outputs,
                                                        _g_inputs)

        # Readable sockets have data ready to read
        for s in readable:
            if s is server:
                # Accept connections
                conn_sock, addr = s.accept()

                # Wait for connections to report its GUID
                conn_sock.setblocking(False)
                _g_inputs.append(conn_sock)

            elif s is _g_recv_kill_sock:
                _g_logger.info('Connection server received kill signal')
                s.recv(RECV_BUF_SZ)  # Clear out dummy data
                done = True  # End server after this iteration of mainloop

            else:
                # Established socket sent data
                rx_data, rx_addr = s.recvfrom(RECV_BUF_SZ)
                _g_logger.info('Connection server received \'%s\' from \'%s\'',
                               rx_data, rx_addr)

                __process_rx_data(rx_addr, rx_data, s, host_guid)

        # Writable sockets have data ready to be sent
        for s in writable:
            # TODO
            pass

        # Exceptional sockets experience 'exceptional condition'
        for s in exceptional:
            # Raise exception if server is 'exceptional'
            # Unreleased resources will get garbage collected by OS
            __cleanup(_g_inputs)

            if s is server:
                _g_logger.critical('Connection server encountered fatal error')
                raise RuntimeError('Connection server encountered fatal error')

            else:
                _g_logger.critical('Non-server socket encountered fatal error')
                raise RuntimeError('Non-server socket encountered fatal error')

    # Cleanup sockets on exit
    __cleanup(_g_inputs)
    _g_logger.info('Connection server closed')


def start(conn_port, host_guid, connection_map):
    '''
    Starts up connection server's mainloop on separate thread
    and returns control to caller.

    :param conn_port: Port for connection server to listen on
    :param host_guid: GUID of local machine
    :param connection_map: Dictionary for tracking active connections
    '''
    global _g_kill_sock
    global _g_recv_kill_sock
    global _g_mainloop_thread
    global _g_connection_map

    opt_val = 1  # For setting socket options

    # Create/Configure TCP socket pair for returning control from 'select'
    _g_kill_sock, _g_recv_kill_sock = socket.socketpair(family=socket.AF_INET)

    _g_kill_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    _g_recv_kill_sock.setsockopt(socket.SOL_SOCKET,
                                 socket.SO_REUSEADDR,
                                 opt_val)
    _g_recv_kill_sock.setblocking(False)

    _g_logger.info('Dummy TCP socket pair created and configured')

    # Create and configure TCP server socket to receive TCP connection requests
    server_addr = ('', conn_port)  # Listen on all interfaces

    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    server.setblocking(False)

    server.bind(server_addr)
    _g_logger.info('TCP connection server socket created and configured')

    # Save reference to the connection map
    _g_connection_map = connection_map

    # Startup server's mainloop and return control to caller
    _g_mainloop_thread = threading.Thread(target=__mainloop,
                                          args=(server, host_guid))
    _g_mainloop_thread.start()


def kill():
    '''
    Gracefully stops the connection server and attempts to
    release thread resources.
    '''
    # Server is only killable if it has been started
    try:
        # 'start' called at least once but thread is inactive
        if not _g_mainloop_thread.is_alive():
            _g_logger.critical('Attempted to kill connection server'
                               ' which has already terminated')

            raise RuntimeError('Cannot kill connection server'
                               ' which has already terminated')
    except NameError:
        # 'start' never called so _g_mainloop_thread not defined
        _g_logger.critical('Attempted to kill connection server'
                           ' which has not been started')

        raise RuntimeError('Cannot kill connection server'
                           ' which has not been started')

    thread_join_timeout = 1.0  # Timeout (in sec.) for joining thread

    # Signal mainloop to exit
    _g_kill_sock.send(b'1')
    _g_kill_sock.close()

    _g_logger.info('Kill signal sent to connection server')

    # Attempt to join mainloop thread
    _g_mainloop_thread.join(timeout=thread_join_timeout)

    # Check if thread was joined in time
    if _g_mainloop_thread.is_alive():
        _g_logger.error('Unable to join connection server\'s thread')
