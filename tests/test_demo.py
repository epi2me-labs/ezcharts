"""Test functions in utils."""
import pytest

from ezcharts import demo

def test_run_demo():
    parser = demo.argparser()
    args = parser.parse_args(["--output", "ezcharts_demo_report.html"])
    demo.main(args)
