"""ezCharts demo."""
import argparse

from ezcharts import util


def main(args):
    """Demo for ezCharts functionality."""
    util.set_basic_logging()
    logger = util.get_named_logger("ezCharts Demo")
    logger.info("Hello world")


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        "aplanat demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--output", default="aplanat_demo_report.html",
        help="Output HTML file.")
    return parser
