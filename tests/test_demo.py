"""Test functions in utils."""

from ezcharts import demo
from ezcharts import ond_demo
from ezcharts import ont_demo


def test_run_demo():
    """Run the main demo, just as a test that plots all run."""
    parser = demo.argparser()
    args = parser.parse_args(["--output", "ezcharts_demo_report.html"])
    demo.main(args)


def test_run_ont_demo():
    """Run the ONT specific demo."""
    parser = ont_demo.argparser()
    args = parser.parse_args(["--output", "ezcharts_ont_demo_report.html"])
    ont_demo.main(args)


def test_run_ond_demo():
    """Run the ONT specific demo."""
    parser = ond_demo.argparser()
    args = parser.parse_args(["--output", "ezcharts_ond_demo_report.html"])
    ond_demo.main(args)
