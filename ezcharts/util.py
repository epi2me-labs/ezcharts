"""The odd helper function."""

import argparse
import logging


def get_named_logger(name):
    """Create a logger with a name.

    :param name: name of logger.
    """
    name = name.ljust(10)[:10]  # so logging is aligned
    logger = logging.getLogger('{}.{}'.format(__package__, name))
    logger.name = name
    return logger


def _log_level():
    """Parser to set logging level and acquire software version/commit."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)

    modify_log_level = parser.add_mutually_exclusive_group()
    modify_log_level.add_argument(
        '--debug', action='store_const',
        dest='log_level', const=logging.DEBUG, default=logging.INFO,
        help='Verbose logging of debug information.')
    modify_log_level.add_argument(
        '--quiet', action='store_const',
        dest='log_level', const=logging.WARNING, default=logging.INFO,
        help='Minimal logging; warnings only.')

    return parser
