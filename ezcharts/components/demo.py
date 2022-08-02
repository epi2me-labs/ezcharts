"""ezCharts demo."""
import argparse

import pandas as pd

import ezcharts as ezc
from ezcharts import util
from ezcharts.types import Plot


def main(args):
    """Demo for ezCharts functionality."""
    util.set_basic_logging()
    logger = util.get_named_logger("ezCharts Demo")

    logger.info("Making chart definition with voodoo")

    df = pd.DataFrame({
        # as laid out in echarts docs for a dataset
        'product': [
            'Matcha Latte', 'Milk Tea', 'Cheese Cocoa', 'Walnut Brownie'],
        '2015': [43.3, 83.1, 86.4, 72.4],
        '2016': [85.8, 73.4, 65.2, 53.9],
        '2017': [93.7, 55.1, 82.5, 39.1]
    })
    # how we'd likely normally have it
    df = df.melt(
        id_vars=['product'], value_vars=['2015', '2016', '2017'],
        var_name='year', value_name='sales')
    p = ezc.scatterplot(data=df, x='year', y='sales', hue='product')
    p.render()

    #p = ezc.lineplot(data=df, x='year', y='sales', hue='product')
    #p.render()


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
