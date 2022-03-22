import sys
import os
import logging
from common.variables import LOG_LEVEL

logger = logging.getLogger('client')
logger.setLevel(LOG_LEVEL)

log_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(module)-6s %(message)s')

stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)

path = os.path.join(os.getcwd(), 'client.log')
file_handler = logging.FileHandler(path, encoding='utf8')
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

if __name__ == '__main__':
    message = 'test_message'
    logger.debug(message)
    logger.info(message)
    logger.warning(message)
    logger.error(message)
    logger.critical(message)
