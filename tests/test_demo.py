"""Test functions in utils."""

from ezcharts import demo


def test_run_demo():
    """Run the demo, just as a test that plots all run."""
    parser = demo.argparser()
    args = parser.parse_args(["--output", "ezcharts_demo_report.html"])
    demo.main(args)
