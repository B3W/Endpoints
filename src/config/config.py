'''
Module defining methods for working with application's configuration
'''
import configparser
import enum
import os


@enum.unique
class ConfigEnum(enum.Enum):
    '''
    Enumeration for mapping INI field strings for easy access
    '''
    RX_PORT = enum.auto()    # INI Section: Communication
    ENCODING = enum.auto()


# Absolute path to the configuration file
_CONFIG_FILE_PATH = os.path.abspath('config.ini')
# Parser for reading/writing to configuration
_parser_handle = configparser.ConfigParser()
# Dictionary of all configuration values read in since last update
_config_map = {}
# Dictionary for conversion between INI field enum and string
_key_map = {ConfigEnum.RX_PORT: 'receive_port',
            ConfigEnum.ENCODING: 'byte_encoding'}


def get_value(key):
    '''
    '''
    # Check key is valid and convert to INI field string
    try:
        key_str = _key_map[key]
    except KeyError:
        # TODO key not found in key map
        raise

    # Get value of key from configuration
    try:
        retval = _config_map[key_str]
    except KeyError:
        # TODO key not found in config
        raise

    return retval


def update():
    '''
    Reads in configuration from disk
    '''
    global _parser_handle  # Globals modified within function
    global _config_map

    # TODO check the configuration file path exists
    _parser_handle.read(_CONFIG_FILE_PATH)

    for sect in _parser_handle.sections():
        _config_map.update(_parser_handle.items(sect))


if __name__ == '__main__':
    update()

    print('Configuration Map')
    print(_config_map)
    print()

    print('Configuration Settings')
    print('RX Port: %d' % (int(get_value(ConfigEnum.RX_PORT))))
    print('Byte Encoding: %s' % (get_value(ConfigEnum.ENCODING)))
