"""Utility for logging activities"""

import os
import logging

LOG_FILE = os.environ.get("LOG_FILE") or "logs.log"


def init_logger(logr):
    """
    Generates a logging object, to log activities in the API.

    Args:
        logr (logger): Logger object of main app.
    """
    # set Logging Format
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # adding file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    logr.addHandler(file_handler)
