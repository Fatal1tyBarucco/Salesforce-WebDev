import logging


class JsonLikeFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        return f"[LEVEL={record.levelname}] " f"[LOGGER={record.name}] " f"{record.getMessage()}"


def build_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(JsonLikeFormatter())

    logger.addHandler(console_handler)

    return logger
