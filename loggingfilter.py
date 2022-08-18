import logging.config


class InfoFilter(logging.Filter):
    """get record only from INFO tag"""

    def filter(self, record):
        return record.levelname == "INFO"
