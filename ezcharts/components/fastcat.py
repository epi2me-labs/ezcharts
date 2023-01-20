"""An ezcharts component for plotting sequence summaries."""
import argparse

import numpy as np
import pandas as pd
from pkg_resources import resource_filename

import ezcharts as ezc
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import Grid, Tabs
from ezcharts.plots import util


class SeqSummary(Snippet):
    """Generate sequence summary plots."""

    def __init__(self, seq_summary, theme='epi2melabs', **kwargs):
        """Create sequence summary componet.

        If seq_summary contains results from multiple samples, each will be
        plotted in its own tab.

        :param seq_summary: A path to a fastcat / bamstats output file or
            DataFrame
        """
        super().__init__(styles=None, classes=None)

        with self:
            tabs = Tabs()
            tab_active = True
            if not isinstance(seq_summary, pd.DataFrame):
                df_all = util.read_files(seq_summary)
            else:
                df_all = seq_summary
            # Out of the intersection of columns between `fastcat` and
            # `bamstats` output, only the column with the read IDs has a
            # different name (`read_id` in `fastcat` and `name` in `bamstats`).
            # Rename to ensure the dataframes produced from either `fastcat` or
            # `bamstats` are consistent.
            if df_all.columns[0] == "name":
                df_all.rename(columns={"name": "read_id"}, inplace=True)
            # the following assumes that `fastcat` / `bamstats` has been run
            # with `-s` which is not necessarily the case (if there was only
            # one sample) --> create a dummy 'sample_name' column if missing
            if 'sample_name' not in df_all.columns:
                df_all['sample_name'] = 'sample'
            for sample_id, df_sample in df_all.groupby('sample_name'):
                with tabs.add_tab(sample_id, tab_active):
                    tab_active = False
                    with Grid(columns=3):
                        EZChart(read_quality_plot(df_sample), theme)
                        EZChart(read_length_plot(df_sample), theme)
                        EZChart(base_yield_plot(df_sample), theme)


def base_yield_plot(
        seq_summary,
        title='Base yield above read length'):
    """Create base yield plot."""
    if not isinstance(seq_summary, pd.DataFrame):
        df = util.read_files(seq_summary)[['read_length']]
    else:
        df = seq_summary
    df = df.sort_values('read_length', ascending=True)
    df = pd.concat(
        (pd.DataFrame.from_dict({'read_length': 0}, orient='index').T, df))

    ylab = 'Yield above length / Gbases'
    xlab = 'Read length / kb'

    # If we have u/int8 or u/int16 cast to float to prevent overflow
    df.read_length = df.read_length.astype('uint64')
    df[ylab] = \
        df.read_length.cumsum()[::-1].values / 1e+9
    df[xlab] = df['read_length'] / 1000

    # No need plot all the points
    if len(df) > 10000:
        step = len(df) // 10000
        df = df.loc[::step, :]

    plt = ezc.lineplot(data=df, x=xlab, y=ylab, hue=None)
    plt.series[0].showSymbol = False
    plt.title = dict(text=title)
    return plt


def read_quality_plot(
        seq_summary, bins=100,
        min_qual=4, max_qual=30, title='Read quality'):
    """Create read quality summary plot."""
    if not isinstance(seq_summary, pd.DataFrame):
        df = util.read_files(seq_summary)[['read_length']]
    else:
        df = seq_summary
    mean_q = np.round(df.mean_quality.mean(), 1)
    median_q = int(df.mean_quality.median())

    plt = ezc.histplot(
        data=df.mean_quality, bins=bins)
    plt.title = dict(
        text=title,
        subtext=f"Mean: {mean_q}. Median: {median_q}")
    plt.xAxis.name = 'Quality score'
    plt.xAxis.min, plt.xAxis.max = min_qual, max_qual
    plt.yAxis.name = 'Number of reads'
    return plt


def read_length_plot(
        seq_summary, min_len=None, max_len=None,
        xlim=(0, None), bins=100, bin_width=None, title='Read length'):
    """Create a read length plot.

    :param seq_summary: summary data from fastcat.
    :param min_len: minimum length.
    :param max_len: maximum length.
    :param xlim: tuple for plotting limits (start, end). A value None will
        trigger calculation from the data.
    :param: bins number of bins

    The minimum and maximum lengths are used only to annotate the plot
    (not filter the data).
    """
    if not isinstance(seq_summary, pd.DataFrame):
        df = util.read_files(seq_summary)[['read_length']]
    else:
        df = seq_summary

    mean_length = int(df['read_length'].mean())
    median_length = int(np.median(df['read_length']))
    max_ = int(np.max(df['read_length']))

    plt = ezc.histplot(data=df.read_length / 1000, bins=bins)
    plt.title = dict(
        text=title,
        subtext=f"Mean: {mean_length}. Median: {median_length}. Max: {max_}")
    plt.xAxis.name = 'Read length / kb'
    plt.yAxis.name = 'Number of reads'
    return plt


def main(args):
    """Entry point to demonstrate a sequence summmary component."""
    comp_title = 'Sequence Summary'
    seq_sum = SeqSummary(args.seq_summary)
    report = ComponentReport(comp_title, seq_sum)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'Sequence summary',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--seq_summary",
        default=resource_filename('ezcharts', "data/test/fastcat.stats.gz"),
        help="Sequence summary TSV from fastcat.")
    parser.add_argument(
        "--output",
        default="seq_summary_report.html",
        help="Output HTML file.")
    return parser
