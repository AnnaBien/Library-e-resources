import logging


def create_logger(name: str, filename: str = 'app_debug.log', level: str = 'info'):
    """

    :param name: Logger name
    :param filename: The name of the log file
    :param level: Logging level
    :return:
    """

    level = level if level.upper() in logging.getLevelNamesMapping().keys() else 'info'
    logger = logging.getLogger(name)
    logging.basicConfig(
        filename=filename,
        encoding='utf-8',
        level=getattr(logging, level.upper())
    )
    return logger
