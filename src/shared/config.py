'''
Module defining logic for utilizing application's configuration
'''
import enum
import json
import os


# ** When adding settings to configuration only this enum and the 'KEY_MAP' **
# ** dictionary need edited                                                 **
@enum.unique
class ConfigEnum(enum.Enum):
    '''Enum providing friendly names for configurations'''
    CONNECTION_PORT = enum.auto()
    BYTE_ENCODING = enum.auto()
    ENDPOINT_GUID = enum.auto()
    ENDPOINT_NAME = enum.auto()
    BROADCAST_PORT = enum.auto()


# Dictionary for conversion between enum and JSON field name
KEY_MAP = {
    ConfigEnum.CONNECTION_PORT: 'tcp_connection_port',
    ConfigEnum.BYTE_ENCODING: 'byte_encoding',
    ConfigEnum.ENDPOINT_GUID: 'endpoint_guid',
    ConfigEnum.ENDPOINT_NAME: 'endpoint_name',
    ConfigEnum.BROADCAST_PORT: 'udp_broadcast_port'
}


class Config(object):
    '''Object holding application's configuration'''
    # Default absolute path to the configuration file
    _config_file_path = os.path.abspath('config.json')
    # Handle for holding configuration data
    _config = None

    @staticmethod
    def get(key):
        '''
        Retrieves the configuration specified by the given key
        '''
        try:
            config_value = Config._config[KEY_MAP[key]]
        except KeyError:
            # TODO act on error?
            raise

        return config_value

    @staticmethod
    def set(key, value):
        '''
        Sets specified configuration to specified value
        '''
        try:
            Config._config[KEY_MAP[key]] = value
        except KeyError:
            # TODO act on error?
            raise

    @staticmethod
    def load(config_path=_config_file_path):
        '''
        Reads in configuration from disk

        :param config_path: Absoulte path to configuration
        '''
        # Validate file path
        if not os.path.isfile(config_path):
            # Create missing configuration file
            with open(config_path, 'w'):
                pass

        # Update configuration
        try:
            with open(config_path, 'r') as json_file:
                Config._config = json.load(json_file)
        except json.JSONDecodeError:
            # File contains invalid JSON
            Config._config = {}

        # Update path to configuration
        Config._config_file_path = config_path

    @staticmethod
    def write():
        '''
        Writes the configuration to disk
        '''
        with open(Config._config_file_path, 'w') as json_file:
            json.dump(Config._config, json_file)


# Testing
if __name__ == '__main__':
    Config.load()

    print('Init Config')
    print('RX Port: %d' % (Config.get(ConfigEnum.CONNECTION_PORT)))
    print('Byte Encoding: %s\n' % (Config.get(ConfigEnum.BYTE_ENCODING)))

    Config.set(ConfigEnum.CONNECTION_PORT, 40000)
    Config.set(ConfigEnum.BYTE_ENCODING, 'utf-16')

    print('Config After Set')
    print('RX Port: %d' % (Config.get(ConfigEnum.CONNECTION_PORT)))
    print('Byte Encoding: %s\n' % (Config.get(ConfigEnum.BYTE_ENCODING)))

    # Config.write()
