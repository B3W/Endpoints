"""
Module providing server for managing Endpoint connections.
Server runs on a separate thread from caller.
"""
import datapassing
import datapassing_protocol as dproto
import logging
import msg
import msgprotocol
import netid
import netpacket
import netprotocol
import queue
import select
import config as c
import socket
import threading

_g_logger = logging.getLogger(__name__)


class Connection(object):
    '''Class defining all data related to a connection'''
    def __init__(self, name, sock):
        self.friendly_name = name
        self.tcp_socket = sock
        self.outmsg_queue = queue.Queue()


def send_text_msg(text_message):
    ''''''
    dst_guid = text_message.destination_id

    if dst_guid == _g_HOST_GUID:
        _g_logger.error("Tried to send text message to self")
        return

    # Construct Endpoint message
    endpoint_msg = msg.Msg(msg.MsgType.ENDPOINT_TEXT_COMMUNICATION,
                           text_message.data,
                           text_message.timestamp)

    encoded_msg = msgprotocol.serialize(endpoint_msg)

    # Construct network packet
    net_pkt = netpacket.NetPacket(_g_HOST_GUID, dst_guid, encoded_msg)

    encoded_pkt = netprotocol.serialize(net_pkt)

    # Queue message to be sent over appropriate socket
    try:
        connection = _g_connection_map[dst_guid]
        connection.outmsg_queue.put_nowait(encoded_pkt)

        if connection.tcp_socket not in _g_outputs:
            _g_outputs.append(connection.tcp_socket)

    except queue.Full:
        _g_logger.error("Unable to send text message")


def attempt_connection(dst_addr, dst_guid, dst_name):
    '''Attempts to make a TCP connection at the given address'''
    # Create socket for connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Attempt connection to destination
    connection_addr = (dst_addr, _g_CONNECTION_PORT)
    sock.connect(connection_addr)

    # Record/Update active connection {GUID: (name, socket)}
    if dst_guid not in _g_connection_map:
        __notify_ui_of_connection(netid.NetID(dst_guid, dst_name))

    connection = Connection(dst_name, sock)
    _g_connection_map[dst_guid] = connection

    sock.setblocking(False)
    _g_inputs.append(sock)

    # Construct Endpoint message
    host_netid = netid.NetID(_g_HOST_GUID,
                             c.Config.get(c.ConfigEnum.ENDPOINT_NAME))

    connection_msg = msg.Msg(msg.MsgType.ENDPOINT_CONNECTION_START,
                             host_netid)
    serialized_msg = msgprotocol.serialize(connection_msg)

    # Construct network packet
    pkt = netpacket.NetPacket(_g_HOST_GUID, dst_guid, serialized_msg)
    serialized_pkt = netprotocol.serialize(pkt)

    # Queue message to be sent over appropriate socket
    try:
        connection.outmsg_queue.put_nowait(serialized_pkt)

        if connection.tcp_socket not in _g_outputs:
            _g_outputs.append(connection.tcp_socket)

    except queue.Full:
        _g_logger.error("Unable to send text message")


def __notify_ui_of_connection(net_id):
    '''Passes connection information to UI'''
    ui_message = dproto.DPConnectionMsg(net_id.guid, net_id.name)
    datapassing.pass_msg(ui_message)


def __notify_ui_of_text_data(guid, timestamp, data):
    '''Passes text data to UI'''
    ui_message = dproto.DPTextMsg(dproto.DPMsgDst.DPMSG_DST_UI,
                                  guid,
                                  timestamp,
                                  data)
    datapassing.pass_msg(ui_message)


def __notify_ui_of_disconnect(net_id):
    '''Notifies UI that an Endpoint has disconnected'''
    ui_message = dproto.DPDisconnectMsg(net_id.guid)
    datapassing.pass_msg(ui_message)


def __cleanup(sockets):
    '''
    Releases socket resources

    :param sockets: List of sockets to cleanup
    '''
    for s in socket:
        s.close()


def __validate_pkt(rx_data):
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
        if net_pkt.src == _g_HOST_GUID:
            valid = False
            _g_logger.error(f'Connection received from self: {net_pkt}')

    return net_pkt, valid


def __process_rx_data(addr, data, sock):
    '''
    '''
    global _g_inputs
    global _g_connection_map

    if data:
        # Make sure received data is a valid packet
        net_pkt, valid = __validate_pkt(data)

        if not valid:
            _g_logger.error("Received invalid packet")
            return

        # Extract message type of the packet's payload
        msg_type = msgprotocol.decode_msgtype(net_pkt.msg_payload)

        if msg_type == msg.MsgType.ENDPOINT_CONNECTION_START:
            # A connection was accepted
            _g_logger.info("Connection accepted")

            message = msgprotocol.deserialize(net_pkt.msg_payload)
            net_id = message.payload

            # Record/Update active connection {GUID: (name, socket)}
            if net_id.guid not in _g_connection_map:
                __notify_ui_of_connection(net_id)

            connection = Connection(net_id.name, sock)
            _g_connection_map[net_id.guid] = connection

        elif msg_type == msg.MsgType.ENDPOINT_TEXT_COMMUNICATION:
            # A connection sent text data
            _g_logger.info("Text data received")

            message = msgprotocol.deserialize(net_pkt.msg_payload)
            text_data = message.payload

            __notify_ui_of_text_data(net_pkt.src, message.timestamp, text_data)
            pass

        elif msg_type == msg.MsgType.ENDPOINT_DISCONNECTION:
            # A connection is getting disconnected
            _g_logger.info("Disconnection reported")

            message = msgprotocol.deserialize(net_pkt.msg_payload)
            net_id = message.payload

            # Report disconnection to UI
            __notify_ui_of_disconnect(net_id)

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


def __mainloop(server):
    '''
    Connection server's mainloop (should be run in separate thread)

    :param server: Server socket for detecting connections
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

                # Connections will report their GUID with a message
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

                __process_rx_data(rx_addr, rx_data, s)

        # Writable sockets have data ready to be sent
        for s in writable:
            msg_queue = None

            for guid, connection in _g_connection_map.items():
                # Check if a connection is associated with this socket
                if connection.tcp_socket is s:
                    # Get the message queue for that connection
                    msg_queue = connection.outmsg_queue
                    break

            if msg_queue is not None:
                try:
                    message = msg_queue.get_nowait()
                except queue.Empty:
                    _g_outputs.remove(s)
                else:
                    s.send(message)

            else:
                _g_outputs.remove(s)

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
    global _g_HOST_GUID
    global _g_kill_sock
    global _g_recv_kill_sock
    global _g_mainloop_thread
    global _g_connection_map
    global _g_CONNECTION_PORT

    _g_CONNECTION_PORT = conn_port
    opt_val = 1  # For setting socket options

    _g_HOST_GUID = host_guid

    # Create/Configure TCP socket pair for returning control from 'select'
    _g_kill_sock, _g_recv_kill_sock = socket.socketpair(family=socket.AF_INET)

    _g_kill_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    _g_recv_kill_sock.setsockopt(socket.SOL_SOCKET,
                                 socket.SO_REUSEADDR,
                                 opt_val)
    _g_recv_kill_sock.setblocking(False)

    _g_logger.info('Dummy TCP socket pair created and configured')

    # Create and configure TCP server socket to receive TCP connection requests
    server_addr = ('', _g_CONNECTION_PORT)  # Listen on all interfaces

    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    server.setblocking(False)

    server.bind(server_addr)
    _g_logger.info('TCP connection server socket created and configured')

    # Save reference to the connection map
    _g_connection_map = connection_map

    # Startup server's mainloop and return control to caller
    _g_mainloop_thread = threading.Thread(target=__mainloop, args=(server,))
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
