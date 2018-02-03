"""
Logging stuff.
"""
import logging


class Scribe:
    """Adds functionality to a class to allow it to log information."""
    logging.basicConfig(level='INFO')

    def __init_subclass__(cls, **_):
        cls.logger: logging.Logger = logging.getLogger(type(cls).__name__)
