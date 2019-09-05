"""
Module providing server for responding to Enpoint broadcasts over LAN.
Server runs on a separate thread from caller.
"""
from message import msgprotocol
from network import netprotocol
import select
import socket
import threading


def kill():
    '''
    Gracefully stops the broadcast server and attempts to
    release thread resources.
    '''
    # Server is only killable if it has been started
    try:
        # 'start' called at least once but thread is inactive
        if not _g_mainloop_thread.is_alive():
            raise RuntimeError('Cannot kill broadcast server'
                               ' which has not been started')
    except NameError:
        # 'start' never called so _g_mainloop_thread not defined
        raise RuntimeError('Cannot kill broadcast server'
                           ' which has not been started')

    thread_join_timeout = 1.0  # Timeout (in sec.) for joining thread

    # Signal mainloop to exit
    _g_kill_sock.send(b'1')
    _g_kill_sock.close()

    # Attempt to join mainloop thread
    _g_mainloop_thread.join(timeout=thread_join_timeout)

    # Check if thread was joined in time
    if _g_mainloop_thread.is_alive():
        # TODO Log error?
        pass


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


def __mainloop(server, kill_sock, host_id, host_ip):
    '''
    Broadcast server's mainloop (should be run in separate thread)

    :param server: Server socket for detecting broadcasts
    :param kill_sock: Socket for receiving requests to stop broadcast server
    '''
    recv_buf_sz = 1024  # Max size of received data in bytes
    opt_val = 1         # For setting socket options
    done = False        # Flag indicating server mainloop should stop
    inputs = [server, kill_sock]    # Sockets to read
    outputs = []                    # Sockets to write
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
                rx_data, rx_addr = s.recvfrom(recv_buf_sz)

                # Check if data available
                if not rx_data:
                    continue  # No data read from socket

                # Check for valid packet
                try:
                    net_pkt = netprotocol.deserialize(rx_data)
                except ValueError:
                    continue  # Invalid packet

                # Sanity check IP addressing
                if net_pkt.src == host_ip or net_pkt.dst != host_ip:
                    continue  # Invalid address(es)

                # Check if message is appropriate type of broadcast
                if msgprotocol.is_connect_broadcast(net_pkt.msg_payload):
                    # TODO Extract information from message
                    # TODO Schedule response
                    # TODO Add device to connections list?
                    pass

            elif s is kill_sock:
                done = True  # End server after this iteration of mainloop
                s.recv(recv_buf_sz)  # Clear out dummy data

        # Writable sockets have data ready to send
        for s in writable:
            # Send out data over socket
            data, addr = msg_queues[s]
            s.sendto(data, addr)

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


def start(port, host_ip, host_id):
    '''
    Starts up broadcast server's mainloop on separate thread
    and returns control to caller.

    :param port: Port for broadcast server to listen on
    :param host_ip: Endpoint NetID for local machine
    :param host_ip: IP address of local machine
    '''
    global _g_kill_sock
    global _g_mainloop_thread

    opt_val = 1  # For setting socket options

    # Create/Configure TCP socket pair for returning control from 'select'
    _g_kill_sock, recv_kill_sock = socket.socketpair(family=socket.AF_INET)

    _g_kill_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    recv_kill_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    recv_kill_sock.setblocking(False)

    # Create and configure UDP server socket to receive UDP broadcasts
    server_addr = ('', port)  # Listen on all interfaces

    server = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, opt_val)
    server.setblocking(False)

    server.bind(server_addr)

    # Startup server's mainloop and return control to caller
    _g_mainloop_thread = threading.Thread(target=__mainloop,
                                          args=(server,
                                                recv_kill_sock,
                                                host_id,
                                                host_ip))
    _g_mainloop_thread.start()
