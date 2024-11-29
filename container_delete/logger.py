import sys
import logging
import google.cloud.logging


CLIENT = google.cloud.logging.Client()
CLIENT.setup_logging()


def create_logger(name: str, level: str = 'info'):
    """

    :param name: Logger name
    :param level: Logging level
    :return:
    """

    level = level if level.upper() in logging.getLevelNamesMapping().keys() else 'info'
    logger = logging.getLogger(name)
    logging.basicConfig(
        stream=sys.stdout,
        encoding='utf-8',
        level=getattr(logging, level.upper())
    )
    return logger
