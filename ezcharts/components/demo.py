"""ezCharts demo."""
import argparse

from ezcharts import Plot
from ezcharts import util


def main(args):
    """Demo for ezCharts functionality."""
    util.set_basic_logging()
    logger = util.get_named_logger("ezCharts Demo")

    logger.info("Making chart definition with voodoo")
    p2 = Plot()
    p2.opt.xAxis.type = "category"
    p2.opt.xAxis.name = "Days of the week"
    p2.opt.xAxis.data = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    p2.opt.yAxis.type = "value"
    p2.opt.series.data = [150, 230, 224, 218, 135, 147, 260]
    p2.opt.series.type = "line"
    print("================")
    print(p2.to_json(indent=2))
    print("================")
    p2.render()


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
