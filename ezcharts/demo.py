"""Run ezCharts demo."""
import argparse

from dominate.tags import p
import pandas as pd
from pkg_resources import resource_filename

import ezcharts as ezc
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.labs import LabsReport
from ezcharts.layout.snippets import Grid
from ezcharts.layout.snippets import Tabs
from ezcharts.plots import util


# Setup simple globals
WORKFLOW_NAME = 'wf-template'
REPORT_TITLE = f'{WORKFLOW_NAME}-report'


def main(args):
    """Demo for ezCharts functionality."""
    util.set_basic_logging()
    logger = util.get_named_logger("ezCharts Demo")

    # Good location to prepare plots
    logger.info('Building plots')

    def example_plot(style="line"):
        """Create example plot."""
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
        if style == "line":
            plot = ezc.lineplot(data=df, x='year', y='sales', hue='product')
        elif style == "scatter":
            plot = ezc.scatterplot(data=df, x='year', y='sales', hue='product')
        else:
            raise ValueError("Unknown plot style")
        return plot

    # Then, time to construct a report
    logger.info('Building report')

    # Example data
    params = resource_filename('ezcharts', "test_data/params.json")
    versions = resource_filename('ezcharts', "test_data/versions.txt")

    # Create report
    report = LabsReport(
        REPORT_TITLE, WORKFLOW_NAME, params, versions)

    with report.add_section(
        "alignment-results", 'Alignment results',
        'Results'
    ):
        # This is the tabbed section with ezcharts!
        tabs = Tabs()
        with tabs.add_tab('Summary', True):
            with Grid():
                EZChart(example_plot(), 'epi2melabs')
                EZChart(example_plot(), 'epi2melabs')
        with tabs.add_tab('Accuracy', False):
            EZChart(example_plot(), 'epi2melabs')
        with tabs.add_tab('Depth', False):
            p('Testing, testing, 1 2 3')

    logger.info('Reticulating splines')
    report.write(args.output)


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