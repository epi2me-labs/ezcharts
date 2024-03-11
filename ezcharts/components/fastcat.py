"""An ezcharts component for plotting sequence summaries."""
import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.api import types as pd_types
from pkg_resources import resource_filename
import sigfig

import ezcharts as ezc
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import DataTable, Grid, Tabs
from ezcharts.plots import util

# Categorical types
CATEGORICAL = pd_types.CategoricalDtype(ordered=True)


class SeqSummary(Snippet):
    """Generate sequence summary plots."""

    def __init__(
            self,
            seq_summary=None,
            histogram_stats_dir=None,
            theme='epi2melabs',
            **kwargs):
        """Create sequence summary component.

        If seq_summary contains results from multiple samples, each will be
        plotted in its own tab.

        :param seq_summary: A path to a fastcat read stats output file or
            DataFrame.
        :param histogram_stats_dir: A path to a directory with fastcat stats histograms
            in per-sample subdirectories.
        :param theme: EPI2ME theme.
        :param kwargs:  options are 'flagstat' and 'bam_summary'.
        """
        super().__init__(styles=None, classes=None)

        with self:
            if seq_summary is not None:
                # Assume the input is in fastcat format. If not, try to import as
                # bamstats format.
                if isinstance(seq_summary, pd.DataFrame):
                    df_all = seq_summary
                else:
                    try:
                        df_all = load_stats(seq_summary, format='fastcat')
                    except ValueError:
                        df_all = load_stats(seq_summary, format='bamstats')
                # Check that the file is not empty
                if df_all.empty:
                    raise pd.errors.EmptyDataError('seq_summary is empty')
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
                if len(df_all['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    draw_all_plots(df_all, theme)
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in df_all.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                draw_all_plots(df_sample, theme)
            else:
                if not histogram_stats_dir:
                    raise ValueError(
                        "If seq_summary is not provided, a histogram stats directory"
                        " path must be provided")
                tabs = Tabs()
                with tabs.add_dropdown_menu():
                    for hist_sample_dir in Path(histogram_stats_dir).iterdir():
                        if not hist_sample_dir.is_dir():
                            continue
                        with tabs.add_dropdown_tab(hist_sample_dir.name):
                            draw_all_plots_precomputed(hist_sample_dir, theme)

            # Create flagstat tables
            if "flagstat" in kwargs:
                if isinstance(kwargs["flagstat"], pd.DataFrame):
                    flagstat = kwargs["flagstat"]
                else:
                    flagstat = load_bamstats_flagstat(kwargs["flagstat"])
                # Check that the file is not empty
                if flagstat.empty:
                    raise pd.errors.EmptyDataError('flagstat is empty')
                # the following assumes that `fastcat` / `bamstats` has been run
                # with `-s` which is not necessarily the case (if there was only
                # one sample) --> create a dummy 'sample_name' column if missing
                if 'sample_name' not in df_all.columns:
                    flagstat['sample_name'] = 'sample'
                if len(flagstat['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    DataTable.from_pandas(flagstat, use_index=False)
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in flagstat.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                DataTable.from_pandas(df_sample, use_index=False)
            # Create bamstats metrics
            if "bam_summary" in kwargs:
                if isinstance(kwargs["bam_summary"], pd.DataFrame):
                    df_all = kwargs["bam_summary"]
                else:
                    df_all = load_stats(kwargs["bam_summary"], format='bamstats')
                # Check that the file is not empty
                if df_all.empty:
                    raise pd.errors.EmptyDataError('seq_summary is empty')
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
                if len(df_all['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    draw_all_plots(df_all, theme)
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in df_all.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                draw_all_plots(df_sample, theme)


def draw_all_plots(seq_summary, theme):
    """Draw all three plots using raw data.

    :param seq_summary: pd.DataFrame containing per-sequence summary information.
    :param theme: EPI2ME theme.
    """
    with Grid(columns=3):
        EZChart(read_quality_plot(seq_summary), theme)
        EZChart(read_length_plot(seq_summary), theme)
        EZChart(base_yield_plot(seq_summary), theme)


def draw_all_plots_precomputed(hist_dir, theme):
    """Draw all three plots using pre-computed histograms.

    :param hist_dir: path to fastcat sample histogram directory.
    :param theme: EPI2ME theme.
    """
    length_hist = pd.read_csv(
        hist_dir / 'length.hist', sep='\t',
        dtype=np.uint64, names=['start', 'end', 'count'])
    quality_hist = pd.read_csv(
        hist_dir / 'quality.hist', sep='\t',
        dtype=np.float64, names=['start', 'end', 'count'])
    with Grid(columns=3):
        EZChart(precomputed_read_quality_plot(quality_hist), theme)
        EZChart(precomputed_read_length_plot(length_hist), theme)
        EZChart(precomputed_base_yield_plot(length_hist), theme)


def base_yield_plot(
        seq_summary,
        title='Base yield above read length'):
    """Create yield plot by plotting total yield above read length.

    :param seq_summary: pd.DataFrame containing per-sequence summary information.
    :param title: Plot title.
    """
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
    if len(df) > 1000:
        step = len(df) // 1000
        # thin the data while keeping the last data point
        df = pd.concat((df.loc[::step, :], df.iloc[[-1]]), axis=0)

    plt = ezc.lineplot(data=df, x=xlab, y=ylab, hue=None)
    plt.series[0].showSymbol = False
    plt.title = dict(
        text=title,
        subtext=f"Total yield: {sigfig.round(df.iloc[0][ylab], sigfigs=3)} Gb"
    )
    return plt


def histogram_median(hist, x='start', y='count'):
    """Calculate the median value from histogram data.

    :param hist: pd.DataFrame with columns [start, end, count].
    :param x: the x-axis variable.
    :param y: the y-axis variable.
    """
    cumsum = np.cumsum(hist[y]).to_numpy()
    mid = cumsum[-1] / 2
    pos = np.searchsorted(cumsum, mid)
    return hist[x][pos]


def precomputed_base_yield_plot(
        hist,
        title='Base yield above read length'):
    """
    Create yield above read length plot from pre-computed histogram data.

    :param hist: pd.DataFrame with columns [start, end, count].
    :param title: plot title.
    """
    # reverse the histogram to so that the longest reads come first
    hist = hist[::-1]

    xlab = 'Read length / kb'
    ylab = 'Yield above length / Gbases'

    # Get read length cumulative sum
    cs = np.cumsum(hist['start'] * hist['count']).to_numpy()
    hist[ylab] = cs / 1e+9
    hist = hist.rename(columns={'start': xlab})
    hist[xlab] = hist[xlab] / 1000

    mid = cs[-1] / 2
    n50_index = np.searchsorted(cs, mid)
    n50 = hist.iat[n50_index, hist.columns.get_loc(xlab)]

    # no need to plot all the points
    if len(hist) > 100:
        step = len(hist) // 100
        # thin the data while keeping the last data point
        subsampled = hist[::step]
        if subsampled.iloc[-1][xlab] != hist.iloc[-1][xlab]:
            subsampled = subsampled.append(hist.iloc[-1])
        hist = subsampled

    plt = ezc.lineplot(x=hist[xlab], y=hist[ylab], hue=None)
    plt.series[0].showSymbol = False
    plt.title = dict(
        text=title,
        subtext=(
            f"Total yield: {sigfig.round(hist[ylab].iloc[0])} "
            f"Gb. N50: {sigfig.round(n50, 3)}kb")
    )
    return plt


def read_quality_plot(
        seq_summary, binwidth=0.2,
        min_qual=4, max_qual=30, title='Read quality'):
    """Create read quality summary plot.

    :param seq_summary: pd.DataFrame containing per-sequence summary information.
    :param binwidth: width of each bin.
    :param min_qual: the minimum quality value to plot.
    :param max_qual: the maximum quality value to plot.
    :param title: title of the plot.
    """
    if not isinstance(seq_summary, pd.DataFrame):
        df = util.read_files(seq_summary)[['mean_quality']]
    else:
        df = seq_summary
    mean_q = np.round(df.mean_quality.mean(), 1)
    median_q = int(df.mean_quality.median())

    plt = ezc.histplot(
        data=df.mean_quality, binwidth=binwidth, binrange=(min_qual, max_qual))
    plt.title = dict(
        text=title,
        subtext=f"Mean: {mean_q}. Median: {median_q}")
    plt.xAxis.name = 'Quality score'
    plt.xAxis.min, plt.xAxis.max = min_qual, max_qual
    plt.yAxis.name = 'Number of reads'
    return plt


def precomputed_read_quality_plot(
        hist, binwidth=0.2,
        min_qual=4, max_qual=30, title='Read quality'):
    """Create read quality summary plot from pre-computed histograms.

    :param hist: pd.DataFrame with columns [start, end, count].
    :param binwidth: width of each bin.
    :param min_qual: the minimum quality value to plot.
    :param max_qual: the maximum quality value to plot.
    :param title: title of the plot.
    """
    median = histogram_median(hist)
    mean_q = np.average(0.5*(hist["start"] + hist["end"]), weights=hist['count'])
    plt = ezc.histplot(
        data=hist['start'], weights=hist['count'],
        binwidth=binwidth, binrange=(min_qual, max_qual))
    plt.title = dict(
        text=title,
        subtext=f"Mean: {mean_q:.1f}. Median: {median:.1f}")
    plt.xAxis.name = 'Quality score'
    plt.xAxis.min, plt.xAxis.max = min_qual, max_qual
    plt.yAxis.name = 'Number of reads'
    return plt


def read_length_plot(
    seq_summary,
    xlim=(0, None),
    quantile_limits=False,
    bins=100,
    bin_width=None,
    title="Read length",
):
    """Create a read length plot.

    :param seq_summary: pd.DataFrame containing per-sequence summary information.
    :param xlim: viewable read length limits.
    :param quantile_limits: if True, xlim is interpreted as quantiles of the data rather
        than absolute values.
    :param bins: number of bins.
    :param bin_width: bin width.
    :param title: plot title.

    The reads will be filtered with `min_len` and `max_len` before calculating the
    histogram. The subtext of the plot title will still show the mean / median / maximum
    of the full data.
    """
    if not isinstance(seq_summary, pd.DataFrame):
        df = util.read_files(seq_summary)[['read_length']]
    else:
        df = seq_summary

    mean_length = int(df['read_length'].mean())
    median_length = int(np.median(df['read_length']))
    max_ = int(np.max(df['read_length']))
    min_ = int(np.min(df['read_length']))

    read_lengths = df['read_length'].values

    min_len, max_len = xlim

    if min_len is None:
        min_len = 0
    if max_len is None:
        max_len = 1 if quantile_limits else read_lengths.max()

    if quantile_limits:
        min_len, max_len = np.quantile(read_lengths, [min_len, max_len])
        # set `xlim` so that we can use it to set the x-axis limits below
        xlim = (min_len, max_len)

    read_lengths = read_lengths[
        (read_lengths >= min_len) & (read_lengths <= max_len)
    ]

    read_lengths = read_lengths / 1000
    if bin_width is not None:
        bin_width /= 1000

    plt = ezc.histplot(data=read_lengths, bins=bins, binwidth=bin_width)
    plt.title = dict(
        text=title,
        subtext=(
            f"Mean: {mean_length:,d}. Median: {median_length:,d}. "
            f"Min: {min_:,d}. Max: {max_:,d}"
        )
    )
    plt.xAxis.name = 'Read length / kb'
    plt.yAxis.name = 'Number of reads'

    if xlim[0] is not None:
        plt.xAxis.min = xlim[0] / 1000
    if xlim[1] is not None:
        plt.xAxis.max = xlim[1] / 1000
    return plt


def precomputed_read_length_plot(
        hist,
        xlim=(0, None),
        quantile_limits=False,
        bins=100,
        bin_width=None,
        title="Read length"):
    """Create a read length plot from pre-computed histogram data.

    :param hist: pd.DataFrame with columns [start, end, count].
    :param xlim: viewable read length limits.
    :param quantile_limits: if True, xlim is interpreted as quantiles of the data
        rather than absolute values.
    :param bins: number of bins.
    :param bin_width: bin width.
    :param title: plot title.

    The reads will be filtered with `min_len` and `max_len` before calculating the
    histogram. The subtext of the plot title will still show the mean / median / maximum
    of the full data.
    """
    min_len, max_len = xlim

    if min_len is None:
        min_len = 0
    if max_len is None:
        max_len = 1 if quantile_limits else hist.iloc[-1]['end']

    if quantile_limits:
        cs = np.cumsum(hist['count'])
        lower_idx, upper_idx = np.searchsorted(
            cs, np.quantile(cs, quantile_limits))
        min_len, max_len = (hist['start'][lower_idx], hist['end'][upper_idx])
        xlim = (min_len, max_len)

    median_length = histogram_median(hist)
    mean_length = np.average(hist['start'], weights=hist['count'])
    max_ = hist.iloc[-1]['end']
    min_ = hist.iloc[0]['start']

    hist = hist[(hist['start'] >= min_len) & (hist['end'] <= max_len)]

    plt = ezc.histplot(
        data=hist['start'] / 1000, bins=bins, binwidth=bin_width, weights=hist['count'])
    plt.title = dict(
        text=title,
        subtext=(
            f"Mean: {mean_length:.1f}. Median: {median_length:.1f}. "
            f"Min: {min_:,d}. Max: {max_:,d}"
        )
    )
    plt.xAxis.name = 'Read length / kb'
    plt.yAxis.name = 'Number of reads'

    if xlim[0] is not None:
        plt.xAxis.min = xlim[0] / 1000
    if xlim[1] is not None:
        plt.xAxis.max = xlim[1] / 1000
    return plt


def load_bamstats_flagstat(flagstat):
    """Load and prepare bamstats flagstat output.

    :param flagstat: path to file(s) containing bamstats flagstat output. Either a
        path to a single file or a path to a directory containing stats files.
    """
    relevant_stats_cols_dtypes = {
        "ref": CATEGORICAL,
        "sample_name": CATEGORICAL,
        "total": int,
        "primary": int,
        "secondary": int,
        "supplementary": int,
        "unmapped": int,
        "qcfail": int,
        "duplicate": int,
    }
    # Prepare input files
    dfs = []
    if os.path.isdir(flagstat):
        input_files = [(flagstat, i) for i in os.listdir(flagstat)]
    elif os.path.isfile(flagstat):
        input_files = [(None, flagstat)]
    else:
        raise Exception(f'No valid input: {flagstat}')
    # If no files, throw error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {flagstat}')
    # Start processing file
    for inpath, fname in input_files:
        try:
            flagstat_file = fname if inpath is None else f'{inpath}/{fname}'
            df = pd.read_csv(
                flagstat_file, sep="\t",
                usecols=relevant_stats_cols_dtypes.keys(),
                dtype=relevant_stats_cols_dtypes)
            # If it's empty, add an empty DF
            if df.empty:
                cols = relevant_stats_cols_dtypes.update(
                    {'Status': str, 'filename': str})
                dfs.append(pd.DataFrame(columns=cols))
                continue
            # Add mapped/unmapped status
            df["Status"] = df["ref"].apply(
                lambda x: "Unmapped" if x == "*" else "Mapped"
            )
            # Add file name
            df['filename'] = fname.split('/')[-1]
            # Append processed DF
            dfs.append(df)
        except pd.errors.EmptyDataError:
            cols = relevant_stats_cols_dtypes.update({'filename': str})
            dfs.append(pd.DataFrame(columns=cols.keys()).astype(cols))
    return pd.concat(dfs).reset_index(drop=True)


def load_stats(stat, format=None):
    """Load and prepare bamstats flagstat.

    :param stat: flagstat file paths. Either a single path to a file, a list/tuple of
        paths, or a path to a directory containing files.
    :param format: stats source: bamstats/fastcat.

    """
    # Input columns for bamstats
    bamstats_cols_dtypes = {
        "name": str,
        "sample_name": CATEGORICAL,
        "ref": CATEGORICAL,
        "coverage": float,
        "ref_coverage": float,
        "read_length": int,
        "mean_quality": float,
        "acc": float,
    }
    # Input columns for fastcat
    fastcat_cols_dtypes = {
        "read_id": str,
        "filename": CATEGORICAL,
        "sample_name": CATEGORICAL,
        "read_length": int,
        "mean_quality": float,
        "channel": int,
        "read_number": int,
        "start_time": str,
    }
    # Infer format
    if format == 'bamstats':
        relevant_stats_cols_dtypes = bamstats_cols_dtypes
        time_cols = None
    elif format == 'fastcat':
        relevant_stats_cols_dtypes = fastcat_cols_dtypes
        time_cols = ['start_time']
    else:
        raise ValueError(f"{format} not valid file type")
    # Prepare input files
    dfs = []
    if isinstance(stat, (list, tuple)) and all([os.path.isfile(path) for path in stat]):
        # got a list of files
        input_files = [(None, file) for file in stat]
    elif os.path.isdir(stat):
        input_files = [(stat, i) for i in os.listdir(stat)]
    elif os.path.isfile(stat):
        input_files = [(None, stat)]
    else:
        raise Exception(f'No valid input: {stat}')
    # If no files, throw error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {stat}')
    # Start processing
    for (inpath, fname) in input_files:
        try:
            fastcat_file = fname if not inpath else f'{inpath}/{fname}'
            df = pd.read_csv(
                fastcat_file,
                sep="\t",
                header=0,
                usecols=relevant_stats_cols_dtypes.keys(),
                dtype=relevant_stats_cols_dtypes,
                parse_dates=time_cols
                )
            # If it's empty, add an empty DF
            if df.empty:
                cols = relevant_stats_cols_dtypes.update(
                    {'filename': str})
                dfs.append(
                    pd.DataFrame(columns=cols).rename(columns={'name': 'read_id'}))
                continue
            # Add file name if missing
            if 'filename' not in df.columns:
                df['filename'] = fname.split('/')[-1]
            # Rename "name" to "read_id"
            if 'read_id' not in df.columns and 'name' in df.columns:
                df.rename(columns={'name': 'read_id'}, inplace=True)
            if format == 'fastcat':
                # Ensure we have datetime format
                # Use utc=true to account for mixed time offsets.
                # This converts dates to UTC.
                # https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
                df['start_time'] = pd.to_datetime(
                    df.start_time, utc=True).dt.tz_localize(None)
            # Append processed DF
            dfs.append(df)
        except pd.errors.EmptyDataError:
            cols = relevant_stats_cols_dtypes.update({'filename': str})
            dfs.append(
                pd.DataFrame(columns=cols.keys()).astype(cols))
    # concatenate and emit
    return pd.concat(dfs).reset_index(drop=True)


def main(args):
    """Entry point to demonstrate a sequence summary component."""
    comp_title = 'Sequence Summary'
    # Define inputs.
    # If seq_summary is not passed, then use bam_readstats
    if args.seq_summary:
        seq_summary = args.seq_summary
    elif args.seq_summary is None and args.bam_readstats is not None:
        seq_summary = args.bam_readstats
    else:
        raise ValueError('No valid input for seq_summary/bam_readstats.')
    if args.seq_summary is not None and args.bam_readstats is not None:
        bam_summary = args.bam_readstats
    else:
        bam_summary = None
    # Create summary
    seq_sum = SeqSummary(
        seq_summary,
        bam_summary=bam_summary,
        flagstat=args.bam_flagstat
        )
    # Write report
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
        "--bam_flagstat",
        default=resource_filename('ezcharts', "data/test/bamstats.flagstat.tsv"),
        help="Bam flagstats TSV from bamstats.")
    parser.add_argument(
        "--bam_readstats",
        default=resource_filename('ezcharts', "data/test/bamstats.readstats.tsv.gz"),
        help="Read statistics TSV from bamstats.")
    parser.add_argument(
        "--output",
        default="seq_summary_report.html",
        help="Output HTML file.")
    return parser
