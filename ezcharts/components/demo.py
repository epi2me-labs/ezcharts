"""ezCharts demo."""
import argparse

from ezcharts import BasePlot
from ezcharts import util


def main(args):
    """Demo for ezCharts functionality."""
    util.set_basic_logging()
    logger = util.get_named_logger("ezCharts Demo")

    logger.info("Making chart definition with voodoo")
    p2 = BasePlot()
    p2.xAxis.type = "category"
    p2.xAxis.data = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    p2.yAxis.type = "value"
    p2.series.data = [150, 230, 224, 218, 135, 147, 260]
    p2.series.type = "line"
    print("================")
    print(p2.to_json(indent=2))
    print("================")


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
