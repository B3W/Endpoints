'''
Module providing various shared network utility functions.
'''
import netifaces
import socket


def get_broadcast_ips():
    '''
    Determines IP addresses for brodcasting

    :returns: List of broadcasting IP addresses (xxx.xxx.xxx.xxx)
    '''
    broadcast_ips = []  # IP addresses for broadcasting
    interface_skip_list = ['127.0.0.1']  # Adapter addresses to skip over

    # Search through network adapters
    for adapter in netifaces.interfaces():
        # Get info from network interfaces for the INET address family
        # Info in the form -> list of dicts of addresses
        try:
            af_inet_info = netifaces.ifaddresses(adapter)[netifaces.AF_INET]
        except KeyError:
            # Interface has no info for INET address family, skip
            continue

        for addr_dict in af_inet_info:
            # Check AF_INET info for broadcasting address
            try:
                if addr_dict['addr'] not in interface_skip_list:
                    broadcast_ips.append(addr_dict['broadcast'])
            except KeyError:
                # No interface or broadcast address, skip
                pass

    return broadcast_ips


def get_host_ip():
    '''
    Determines the primary address for host. No internet connection required.

    :returns: Primary IP address for host (xxx.xxx.xxx.xxx)
              or '127.0.0.1' if it cannot be determined
    '''
    connection_addr = ('10.255.255.255', 1)  # Address for querying host's IP
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    try:
        # Attempt connection
        sock.connect(connection_addr)

        # Connection successful, get IP from local socket
        host_ip = sock.getsockname()[0]

    except Exception:
        # Fallback to loopback if no other found
        host_ip = '127.0.0.1'

    finally:
        sock.close()

    return host_ip
