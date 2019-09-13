'''
Module providing various shared utility functions and classes.
'''
import collections
import netifaces
import socket
import threading


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


class SynchronizedDict(collections.MutableMapping):
    '''
    Class representing simple, synchronized dictionary
    '''
    def __init__(self, *args, **kwargs):
        self._map = dict()              # Structure for storing data
        self.update(dict(*args, **kwargs))
        self._lock = threading.RLock()  # Access lock

    @classmethod
    def fromkeys(cls, iterable, value=None):
        sync_dict = SynchronizedDict()

        sync_dict._map = dict.fromkeys(iterable, value)

        return sync_dict

    def __getitem__(self, key):
        with self._lock:
            item = self._map[key]

        return item

    def __setitem__(self, key, value):
        with self._lock:
            self._map[key] = value

    def __delitem__(self, key):
        with self._lock:
            del self._map[key]

    def __iter__(self):
        with self._lock:
            it = iter(self._map)

        return it

    def __len__(self):
        with self._lock:
            length = len(self._map)

        return length

    def __str__(self):
        with self._lock:
            s = str(self._map)

        return s
