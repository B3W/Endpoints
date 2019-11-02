'''Entry point for Endpoints application'''
from discovery import netfind, netserve
import errno
import logging
from network import netid
import os
import platform
import queue
from shared import config as c
from shared import synceddict as sd
from shared import timeutils
import uuid


if __name__ == '__main__':
    # Get path to this module
    main_path = os.path.dirname(os.path.abspath(__file__))

    # Initialize logging module
    log_name = 'Endpoint-Log-%s.log' % timeutils.get_iso_timestamp()
    log_dir = os.path.join(main_path, '.logs')

    try:
        os.makedirs(log_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    log_path = os.path.join(log_dir, log_name)

    logging.basicConfig(filename=log_path, filemode='w',
                        format='%(asctime)s'
                               ' %(levelname)s(%(name)s): %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)

    logger = logging.getLogger(__name__)  # Retrieve module logger

    # Construct configuration path and load configuration
    config_path = os.path.join(main_path, 'config.json')
    c.Config.load(config_path)

    # Construct host's GUID
    encoding = c.Config.get(c.ConfigEnum.BYTE_ENCODING).strip()

    try:
        guid = c.Config.get(c.ConfigEnum.ENDPOINT_GUID)
    except KeyError:
        guid = uuid.uuid4().int  # Generate random GUID
        c.Config.set(c.ConfigEnum.ENDPOINT_GUID, guid)  # Write to config

    logger.debug('GUID: %s', str(guid))

    # Construct machine's NetID
    missing = False
    try:
        ep_name = c.Config.get(c.ConfigEnum.ENDPOINT_NAME).strip()
    except KeyError:
        missing = True

    if missing or len(ep_name) == 0:
        # Use machine name if none specified in configuration
        # Try to get machine name via env vars, fallback to platform.node
        ep_name = os.getenv('HOSTNAME',
                            os.getenv('COMPUTERNAME', platform.node()))

        c.Config.set(c.ConfigEnum.ENDPOINT_NAME, ep_name)

    host_netid = netid.NetID(ep_name)
    logger.debug('NetID: %s', host_netid)

    # Retreive message ports
    try:
        conn_port = c.Config.get(c.ConfigEnum.CONNECTION_PORT)
    except KeyError:
        conn_port = 3434
        c.Config.set(c.ConfigEnum.CONNECTION_PORT, conn_port)

    logger.debug('Connection Port: %d', conn_port)

    try:
        msg_port = c.Config.get(c.ConfigEnum.MESSAGE_PORT)
    except KeyError:
        msg_port = 3435
        c.Config.set(c.ConfigEnum.MESSAGE_PORT, msg_port)

    logger.debug('Message Port: %d', msg_port)
    logger.info('Loaded configuration from %s', config_path)

    # Initialize map for tracking connected devices - {GUID: (IP, name)}
    endpoint_map = sd.SyncedDict()

    # Initialize data passing queues
    backend_queue = queue.Queue()  # Data -> backend services
    ui_queue = queue.Queue()  # Data -> UI

    # Start UDP listener for connection broadcasts
    netserve.start(conn_port, guid, host_netid, endpoint_map, ui_queue)
    logger.info('Background connection service started')

    # TODO Start up background message service

    # TODO Start up queue message handler

    # Broadcast discovery message over network adapters
    netfind.execute(conn_port, guid, host_netid)
    logger.info('Discovery message broadcasting complete')

    # TODO Start up UI in main thread

    # Write configuration back to disk
    # c.Config.write()
