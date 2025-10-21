import logging


def get_logger(name: str = "GIArchive", verbose: bool = False):
    """Returns a common logger

    :param name: _description_, defaults to "GIArchive"
    :param verbose: _description_, defaults to False
    :return: _description_
    """
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.setLevel(level=logging.INFO if not verbose else logging.debug)
    return logger
