import logging
from functools import wraps
import sys


def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger_name = 'server' if 'server.py' in sys.argv[0] else 'client'
        LOGGER = logging.getLogger(logger_name)
        LOGGER.debug(f'Вызов функции "{func.__name__}" с параметрами: {args}, {kwargs}')
        result = func(*args, **kwargs)
        return result

    return wrapper
