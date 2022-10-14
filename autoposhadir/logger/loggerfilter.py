import logging.config


class DebugFilter(logging.Filter):
    """get record only from DEBUG tag"""

    def filter(self, record):
        return (
            not (record.levelname == "INFO")
            or (record.levelname == "WARNING")
            or (record.levelname == "ERROR")
            or (record.levelname == "CRITICAL")
        ) and ((record.name == "__main__") or (record.name == "presensi"))


class InfoFilter(logging.Filter):
    """get record only from INFO tag"""

    def filter(self, record):
        return (
            not (record.levelname == "DEBUG")
            or (record.levelname == "WARNING")
            or (record.levelname == "ERROR")
            or (record.levelname == "CRITICAL")
        )
