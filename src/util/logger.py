import logging


class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors based on log level."""

    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[1;31m",  # Bold Red
    }
    RESET = "\033[0m"

    def format(self, record):
        log_color = self.COLORS.get(record.levelno, self.RESET)
        levelname_colored = f"{log_color}{record.levelname}{self.RESET}"
        message_colored = f"{log_color}{record.getMessage()}{self.RESET}"
        record.levelname = levelname_colored
        record.msg = message_colored
        return super().format(record)


def get_logger(name: str = "GIArchive", verbose: bool = False):
    """Returns a common logger

    :param name: _description_, defaults to "GIArchive"
    :param verbose: _description_, defaults to False
    :return: _description_
    """
    logger = logging.getLogger(name)
    logger.setLevel(level=logging.INFO if not verbose else logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter("[%(levelname)s] %(message)s"))
        logger.addHandler(handler)
    return logger
