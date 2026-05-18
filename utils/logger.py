"""
utils/logger.py
---------------
Custom colored logger for the framework.
Provides consistent log formatting across all modules.
"""

import logging

import colorlog


def get_logger(name: str) -> logging.Logger:
    """
    Create and return a colored logger instance.

    Args:
        name: Logger name, typically the module's __name__.

    Returns:
        Configured Logger instance with color formatting.
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            fmt="%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            }
        )
    )

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers when logger is reused
    if not logger.handlers:
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)
    return logger
