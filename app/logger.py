import logging
import sys


def configure_logging(level_name: str = "INFO") -> None:
    """Configure application-wide logging."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    root_logger = logging.getLogger()

    if getattr(configure_logging, "_configured", False):
        root_logger.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)
    configure_logging._configured = True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
