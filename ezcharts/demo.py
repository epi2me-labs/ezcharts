"""Run ezCharts demo."""
import argparse

from dominate.tags import p
import numpy as np
import pandas as pd
from pkg_resources import resource_filename

import ezcharts as ezc
from ezcharts import util
from ezcharts.components.ezchart import EZChart
from ezcharts.components.fastcat import SeqSummary
from ezcharts.components.nextclade import NextClade, NXTComponent
from ezcharts.components.reports.labs import LabsReport
from ezcharts.components.theme import LAB_head_resources
from ezcharts.layout.snippets import Grid
from ezcharts.layout.snippets import OffCanvas
from ezcharts.layout.snippets import Progress
from ezcharts.layout.snippets import Stats
from ezcharts.layout.snippets import Tabs
from ezcharts.layout.snippets.cards import Cards
from ezcharts.layout.snippets.cards import ICard
from ezcharts.plots import Plot
from ezcharts.plots.ideogram import ideogram

# Setup simple globals
WORKFLOW_NAME = 'wf-template'
REPORT_TITLE = f'{WORKFLOW_NAME}-report'


def main(args):
    """Demo for ezCharts functionality."""
    logger = util.get_named_logger("ezChrtDemo")

    # Good location to prepare plots
    logger.info('Building plots')

    def example_plot(style="line") -> Plot:
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
        elif style == 'histogram':
            plot = ezc.histplot(
                data=np.random.randint(0, 11, size=1000), bins=10)
        elif style == "bar":
            plot = ezc.barplot(data=df, x='year', y='sales', hue='product')
        else:
            raise ValueError("Unknown plot style")
        plot.title = {"text": f"Example {style} chart"}
        return plot

    # Then, time to construct a report
    logger.info('Building report')

    # Example data
    params = resource_filename('ezcharts', "data/test/params.json")
    versions = resource_filename('ezcharts', "data/test/versions.txt")
    nxt_json = resource_filename('ezcharts', "data/test/nextclade.json")
    fastcat_results = resource_filename(
        'ezcharts', "data/test/fastcat.stats.gz")

    # Create report
    # Note we need to add nextclade as a resource
    report = LabsReport(
        REPORT_TITLE, WORKFLOW_NAME, params, versions,
        head_resources=[*LAB_head_resources, NXTComponent])

    # Add a header badge via a method on the report element.
    report.add_badge('Test badge', bg_class="bg-primary")

    # Make a progress bar for the median accuracy box
    median_accuracy = Progress(
            value_min=0,
            value_max=100,
            value_now=98.9,
            bar_cls="progress-bar-striped",
            height=50)

    # Add something directly to main_content.
    with report.main_content:
        # Stats is a snippet, but we could also just add any html
        # tags here. Snippets are little reusable portions of html,
        # styles and or scripts in python class format. They often
        # expose methods for adding content to them in a simple way.
        # E.g.
        Stats(
            columns=3,
            items=[
                ('1213986', 'Read count'),
                (median_accuracy, 'Median accuracy'),
                ('10213 bp', 'Some other stat')
            ])

    # Add sequence summary component
    with report.add_section('Sequence summaries', 'Summaries'):
        SeqSummary(fastcat_results)

    # This also adds to main_content, but provides a nice
    # container snippet as a starting context.
    with report.add_section('Controls', 'Controls'):
        # This is an example of how to use bootstrap cards
        Cards(
            columns=2,
            items=[
                ICard(
                    head="Positive",
                    body="The positive passed",
                    footer="All postive controls within threshold",
                    classes="bg-success text-white"),
                ICard(
                    head="No Template Control",
                    body="The NTC failed",
                    footer="NTC outside set thresholds.",
                    classes="bg-danger text-white")])
        OffCanvas(
            label="More details (Offcanvas demo)",
            title="Details of Controls",
            body="You can put more details here....")

    # This also adds to main_content, but provides a nice
    # container snippet as a starting context.
    with report.add_section('Alignment results', 'Results'):
        # This is the tabbed section with ezcharts!
        tabs = Tabs()
        with tabs.add_tab('Summary', True):
            # Grids are snippets that provide responsive
            # layouts via css grid
            with Grid():
                EZChart(example_plot("line"), 'epi2melabs')
                EZChart(example_plot("scatter"), 'epi2melabs')
                EZChart(example_plot("bar"), 'epi2melabs')
                EZChart(example_plot("histogram"), 'epi2melabs')
        with tabs.add_tab('Accuracy', False):
            p("This is a mixed tab!")
            EZChart(example_plot(), 'epi2melabs')
        with tabs.add_tab('Depth', False):
            p('Testing, testing, 1 2 3')

        # Dropdowns are nested one more level
        with tabs.add_dropdown_menu('Example'):
            with tabs.add_dropdown_tab('First', False):
                EZChart(example_plot(), 'epi2melabs')

    with report.add_section('Nextclade results', 'Nextclade', True):
        NextClade(nxt_json)

    with report.add_section('Human Genome', 'Genome'):
        EZChart(
            ideogram(blocks='cytobands'),
            'epi2melabs', height="800px")

    logger.info('Reticulating splines')
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        "ezcharts demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--output", default="ezcharts_demo_report.html",
        help="Output HTML file.")
    return parser
