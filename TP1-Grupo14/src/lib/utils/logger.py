import logging

_loggers = {}


def setup_logger(verbose=False, quiet=False, name="file-transfer"):
    if name in _loggers:
        return

    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if quiet:
        logger.setLevel(logging.ERROR)
    elif verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    _loggers[name] = logger


def get_logger(name="file-transfer"):
    return logging.getLogger(name)
