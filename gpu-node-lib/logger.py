import logging
import sys

logger = None


def setup_logger():
    """
    This function sets up a logger.

    :return: logger object
    :rtype: object
    """
    global logger
    if logger:
        return logger

    logger = logging.getLogger()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s[%(levelname)s]:(%(name)s) - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
