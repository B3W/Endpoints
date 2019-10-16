'''
'''
import collections
import threading


class SyncedDict(collections.MutableMapping):
    '''
    Class representing simple, synchronized dictionary
    '''
    def __init__(self, *args, **kwargs):
        self._map = dict()              # Structure for storing data
        self.update(dict(*args, **kwargs))
        self._lock = threading.RLock()  # Access lock

    @classmethod
    def fromkeys(cls, iterable, value=None):
        sync_dict = SyncedDict()

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
