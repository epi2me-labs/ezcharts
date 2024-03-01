"""Test functions in utils."""
import pytest

import argparse
import logging

from ezcharts import util

# examples of how not to write tests

def test_create_logger():
    """Make a logger."""
    logger = util.get_named_logger("MyLogger")
    assert isinstance(logger, logging.Logger)


def test_set_log_level():
    """Make a parser."""
    parser = util._log_level()
    assert isinstance(parser, argparse.ArgumentParser)
