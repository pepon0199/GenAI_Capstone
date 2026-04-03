import logging
import os


def configure_logging():
    level_name = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=False,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
