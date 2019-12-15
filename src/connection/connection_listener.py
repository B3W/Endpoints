"""
Module providing server for serving to Enpoint conversation connections.
Server runs on a separate thread from caller.
"""
import logging
import select
import socket
import threading

_g_logger = logging.getLogger(__name__)


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
                               ' which has not been started')

            raise RuntimeError('Cannot kill connection server'
                               ' which has not been started')
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

    _g_logger.info('Broadcast server closed')


def __cleanup(sockets):
    '''
    Releases socket resources

    :param sockets: List of sockets to cleanup
    '''
    for s in socket:
        s.close()


def __mainloop(server, conn_port, host_guid, connection_queue):
    '''
    Broadcast server's mainloop (should be run in separate thread)

    :param server: Server socket for detecting broadcasts
    :param conn_port: Port connection servers are listening over
    :param host_guid: GUID of local machine
    :param connection_queue: Queue for writing new connections into
    '''
    _g_logger.info('Connection server\'s mainloop started')

    recv_buf_sz = 1024  # Max size of received data in bytes
    done = False        # Flag indicating server mainloop should stop
    inputs = [server, _g_recv_kill_sock]    # Sockets to read

    while inputs and not done:
        # Multiplex with 'select' call
        readable, _, exceptional = select.select(inputs, [], inputs)

        # Readable sockets have data ready to read
        for s in readable:
            if s is server:
                # Accept new connection
                conn_sock, addr = s.accept()

                # Pass new connection to comm manager
                # TODO

            elif s is _g_recv_kill_sock:
                _g_logger.info('Connection server received kill signal')
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
                _g_logger.critical('Connection server encountered fatal error')
                raise RuntimeError('Connection server encountered fatal error')

            else:
                _g_logger.critical('Non-server socket encountered fatal error')
                raise RuntimeError('Non-server socket encountered fatal error')

    # Cleanup sockets on exit
    __cleanup(inputs)
    _g_logger.info('Connection server closed')


def start(conn_port, host_guid, connection_queue):
    '''
    Starts up connection server's mainloop on separate thread
    and returns control to caller.

    :param conn_port: Port for connection server to listen on
    :param host_guid: GUID of local machine
    :param connection_queue: Queue for writing new connections into
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
    server_addr = ('', conn_port)  # Listen on all interfaces

    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    server.setblocking(False)

    server.bind(server_addr)
    _g_logger.info('TCP connection server socket created and configured')

    # Startup server's mainloop and return control to caller
    _g_mainloop_thread = threading.Thread(target=__mainloop,
                                          args=(server,
                                                conn_port,
                                                host_guid,
                                                connection_queue))
    _g_mainloop_thread.start()
