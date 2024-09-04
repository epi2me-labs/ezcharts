"""An ezcharts component make plots from the metadata.json."""

import argparse
import json

from bokeh.models import HoverTool
import pandas as pd

import ezcharts as ezc
from ezcharts.components import ezchart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.plots.util import Colors


class PlotMetaData(Snippet):
    """A meta data plotting report component for outputs in meta_data.json."""

    TAG = 'meta-plots'

    def __init__(
            self,
            metadata_json,
            **kwargs
    ) -> None:
        """Initialize a meta plots instance."""
        super().__init__(
            styles=None,
            classes=None)

        # Read count bar plot from the counts in the JSON.
        with self:
            read_count_barplot(metadata_json, **kwargs)


def read_count_barplot(
        metadata_json,
        orient='h',
        fill_color=Colors.cerulean,
        line_color=Colors.cerulean,
        theme='epi2melabs'):
    """Plot per sample read count bar chart."""
    # Per barcode read count
    with open(metadata_json) as data_file:
        data = json.load(data_file)
    barcode_counts = pd.DataFrame(data) \
        .rename(columns={'n_seqs': 'Number of reads', 'alias': 'Sample'})
    order = barcode_counts["Sample"].tolist()
    order.sort()
    if orient == 'h':
        order = order[::-1]
        plt = ezc.barplot(
            data=barcode_counts, x='Number of reads', y='Sample',
            order=order, orient=orient,
            fill_color=fill_color, line_color=line_color)
        hover = plt._fig.select(dict(type=HoverTool))
        hover.tooltips = [("Number of reads", "@right")]
    else:
        plt = ezc.barplot(
            data=barcode_counts, x='Sample', y='Number of reads',
            order=order, orient=orient,
            fill_color=fill_color, line_color=line_color)
        hover = plt._fig.select(dict(type=HoverTool))
        hover.tooltips = [("Number of reads", "@top")]
    ezchart.EZChart(
        plt,
        theme=theme)


def main(args):
    """Entry point to create a report from meta data JSON."""
    meta_data_plots = PlotMetaData(args.metadata)
    read_count_barplot(args.metadata)
    report = ComponentReport(
        'Meta Plots', meta_data_plots)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'Meta Plots',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        "--metadata",
        help="Meta data json."
    )
    parser.add_argument(
        "--output",
        default="readscounts.html",
        help="Output HTML file."
    )
    return parser
