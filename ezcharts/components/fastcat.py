"""An ezcharts component for plotting sequence summaries."""
import argparse
import copy
import os

import numpy as np
import pandas as pd
from pkg_resources import resource_filename
import sigfig

import ezcharts as ezc
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import DataTable, Grid, Tabs


FASTCAT_COLS_DTYPES = {
    "read_id": str,
    "filename": "category",
    "sample_name": "category",
    "read_length": int,
    "mean_quality": float,
    "channel": int,
    "read_number": int,
    "start_time": str,
}

BAMSTATS_COLS_DTYPES = {
    "name": str,
    "sample_name": "category",
    "ref": "category",
    "coverage": float,
    "ref_coverage": float,
    "qstart": "Int64",
    "qend": "Int64",
    "rstart": "Int64",
    "rend": "Int64",
    "aligned_ref_len": "Int64",
    "direction": "category",
    "length": int,
    "read_length": int,
    "mean_quality": float,
    "start_time": str,
    "match": int,
    "ins": int,
    "del": int,
    "sub": int,
    "iden": float,
    "acc": float,
    "duplex": int,
}

BAMSTATS_FLAGSTAT_COLS_DTYPES = {
    "ref": "category",
    "sample_name": "category",
    "total": int,
    "primary": int,
    "secondary": int,
    "supplementary": int,
    "unmapped": int,
    "qcfail": int,
    "duplicate": int,
    "duplex": int,
    "duplex_forming": int,
}

TIMES = ["start_time"]


def _intersect_columns(base, requested=None):
    # Take one of the dtype dictionaries and intersect with a list
    cols = base
    if requested is not None:
        if invalid_cols := set(requested) - set(base.keys()):
            raise ValueError(f"Found unexpected columns {invalid_cols}.")
        cols = {col: base[col] for col in requested}
    times = [t for t in TIMES if t in cols]
    if len(times) == 0:
        times = None
    return cols, times


def _localize_time(df):
    # ensure we have datetime format, convert to utc
    for t in TIMES:
        if t in df.columns:
            df[t] = pd.to_datetime(df.start_time, utc=True).dt.tz_localize(None)
    return df


class SeqSummary(Snippet):
    """Generate sequence summary plots."""

    def __init__(
        self,
        seq_summary,
        flagstat=None,
        sample_names=None,
        theme="epi2melabs",
        color=None,
    ):
        """Create sequence summary component.

        :param seq_summary: a path to a fastcat/bamstats read stats output file
            or dataframe (or a tuple of such).
        :param flagstat: a path to a bamstats flagstat output file or dataframe
            (or tuple of such).
        :sample_names: tuple of sample names. Required when other input arguments
            are tuples.
        :param theme: String defining the visual theme for the plots.
        """
        super().__init__(styles=None, classes=None)
        self.theme = theme

        # we need at least seq_summary or histograms
        if not (
                isinstance(seq_summary, pd.DataFrame)
                or isinstance(seq_summary, str)
                or isinstance(seq_summary, tuple)):
            raise ValueError(
                "`seq_summary` must be a path to a fastcat/bamstats read stats output "
                "file or dataframe, or histogram directories (or a tuple of such).")

        # check sample_names is a tuple if files are provided in tuples.
        if (isinstance(seq_summary, tuple)) and not isinstance(sample_names, tuple):
            raise ValueError(
                "`sample_names` must be provided as a tuple "
                "when more than one input provided.")

        # check tuples are all the same length
        if isinstance(sample_names, tuple) and (len(sample_names) != len(seq_summary)):
            raise ValueError(
                "`sample_names` must have the same length as `seq_summary`.")
        if (
                (flagstat is not None)
                and isinstance(flagstat, tuple)
                and (len(sample_names) != len(flagstat))):
            raise ValueError(
                "`sample_names` must have the same length as `flagstat`.")

        with self:
            if isinstance(seq_summary, tuple):
                # several samples => use a dropdown
                tabs = Tabs()
                with tabs.add_dropdown_menu():
                    for sample_name, data in zip(sample_names, seq_summary):
                        with tabs.add_dropdown_tab(sample_name):
                            self._draw_summary_plots(data, color)
            else:
                # single sample
                self._draw_summary_plots(seq_summary, color)

            # same again for flagstat
            if flagstat is not None:
                if isinstance(flagstat, tuple):
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_name, data in zip(sample_names, flagstat):
                            with tabs.add_dropdown_tab(sample_name):
                                self._draw_flagstat_table(data)
                else:
                    self._draw_flagstat_table(flagstat)

    def _draw_summary_plots(self, data, color):
        """Draw quality, read_length, yield plots using raw data.

        :param seq_summary: pd.DataFrame containing per-sequence summary information.
        :param theme: EPI2ME theme.
        """
        # data is either a summary file, a dataframe (of a summary file),
        # or a directory (of histogram files).
        qdata, ldata = None, None
        if isinstance(data, pd.DataFrame):
            qdata, ldata = data, data
        else:
            try:
                df = load_stats(data)
                qdata, ldata = df, df
            except Exception:
                try:
                    qdata = load_histogram(data, "quality")
                    ldata = load_histogram(data, "length")
                except Exception:
                    raise ValueError("Could not load input data.")

        with Grid(columns=3):
            EZChart(read_quality_plot(qdata, color=color), self.theme)
            EZChart(read_length_plot(ldata, color=color), self.theme)
            EZChart(base_yield_plot(ldata, color=color), self.theme)

    def _draw_bamstat_table(self, data):
        if not isinstance(data, pd.DataFrame):
            data = load_bamstats_flagstat(data)
        DataTable.from_pandas(data, use_index=False)


@ezc.plots.util.plot_wrapper
def base_yield_plot(data, color=None):
    """Create yield plot by plotting total yield above read length.

    :param data: fastcat/bamstats summary data or read-length histogram data.
    """
    xlab = "Read length / kb"
    ylab = "Yield above length / Gbases"
    thinning = None  # don't really know why this is different
    # note: we want an anticumulative sum, hence all the [::-1]
    if "read_length" in data.columns:
        # need to create the data
        thinning = 1000
        length = np.concatenate(([0], np.sort(data["read_length"])), dtype="int")
        cumsum = np.cumsum(length[::-1])[::-1]
    else:
        # assume histogram
        # TODO: this assumes even bins
        thinning = 100
        length = data["start"]
        cumsum = np.cumsum(
            data["start"][::-1].to_numpy() * data["count"][::-1].to_numpy()
        )[::-1]

    mid = cumsum[-1] / 2
    n50_index = np.searchsorted(cumsum, mid)
    n50 = length[n50_index]

    # TODO: we needn't create this only to thin it immediately
    df = pd.DataFrame({xlab: length / 1000, ylab: cumsum / 1e9}, copy=False)

    # thin the data while keeping last
    if len(df) > thinning:
        step = len(df) // thinning
        df = pd.concat((df.loc[::step, :], df.iloc[[-1]]), axis=0)

    plt = ezc.lineplot(data=df, x=xlab, y=ylab, hue=None, color=color)
    plt.series[0].showSymbol = False
    plt.title = dict(
        text="Base yield above read length",
        subtext=(
            f"Total yield: {sigfig.round(df.iloc[0][ylab], sigfigs=3)} Gb "
            f"Gb. N50: {sigfig.round(n50, 3)}kb"
        ),
    )
    return plt


@ezc.plots.util.plot_wrapper
def read_quality_plot(data, binwidth=0.2, min_qual=4, max_qual=30, color=None):
    """Create read quality summary plot.

    :param data: fastcat/bamstats summary data or read-length histogram data.
    :param binwidth: width of each bin.
    :param min_qual: the minimum quality value to plot.
    :param max_qual: the maximum quality value to plot.
    :param title: title of the plot.
    """
    plt, mean_q, median_q = None, None, None
    if "read_length" in data.columns:
        # fastcat/bamstats
        mean_q = np.round(data.mean_quality.mean(), 1)
        median_q = int(data.mean_quality.median())
        plt = ezc.histplot(
            data=data.mean_quality,
            binwidth=binwidth,
            binrange=(min_qual, max_qual),
            color=color
        )
    else:
        # histogram
        mean_q = np.round(
            np.average(0.5 * (data["start"] + data["end"]), weights=data["count"]), 1
        )
        median_q = int(histogram_median(data))
        plt = ezc.histplot(
            data=data["start"],
            weights=data["count"],
            binwidth=binwidth,
            binrange=(min_qual, max_qual),
            color=color
        )

    plt.title = dict(
        text="Read quality", subtext=f"Mean: {mean_q:.1f}. Median: {median_q:.1f}"
    )
    plt.xAxis.name = "Quality score"
    plt.xAxis.min, plt.xAxis.max = min_qual, max_qual
    plt.yAxis.name = "Number of reads"
    return plt


@ezc.plots.util.plot_wrapper
def read_length_plot(
    data, xlim=(0, None), quantile_limits=False, bins=100, binwidth=None, color=None
):
    """Create a read length plot.

    :param seq_summary: pd.DataFrame containing per-sequence summary information.
    :param xlim: viewable read length limits.
    :param quantile_limits: if True, xlim is interpreted as quantiles of the data rather
        than absolute values.
    :param bins: number of bins.
    :param binwidth: bin width.
    :param title: plot title.

    The reads will be filtered with `min_len` and `max_len` before calculating the
    histogram. The subtext of the plot title will still show the mean / median / maximum
    of the full data.
    """
    plt, mean_length, median_length = None, None, None
    min_len, max_len = xlim
    if min_len is None:
        min_len = 0
    # create data to plot depending on input type.
    if "read_length" in data.columns:
        # fastcat/bamstats
        mean_length = np.round(data.read_length.mean(), 1)
        median_length = int(data.read_length.median())
        max_ = int(np.max(data["read_length"]))
        min_ = int(np.min(data["read_length"]))
        read_lengths = data["read_length"].values

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
        if binwidth is not None:
            binwidth /= 1000
        plt = ezc.histplot(data=read_lengths, bins=bins, binwidth=binwidth, color=color)
    else:
        # histogram
        if max_len is None:
            max_len = 1 if quantile_limits else data.iloc[-1]["end"]
        if quantile_limits:
            cs = np.cumsum(data["count"])
            lower_idx, upper_idx = np.searchsorted(cs, np.quantile(cs, quantile_limits))
            min_len, max_len = (data["start"][lower_idx], data["end"][upper_idx])
            xlim = (min_len, max_len)

        median_length = histogram_median(data)
        mean_length = np.average(data["start"], weights=data["count"])
        max_ = data.iloc[-1]["end"]
        min_ = data.iloc[0]["start"]
        data = data[(data["start"] >= min_len) & (data["end"] <= max_len)]
        plt = ezc.histplot(
            data=data["start"] / 1000,
            bins=bins,
            binwidth=binwidth,
            weights=data["count"],
            color=color
        )

    # customize the plot
    plt.title = dict(
        text="Read Length",
        subtext=(
            f"Mean: {mean_length:.1f}. Median: {median_length:.1f}. "
            f"Min: {min_:,d}. Max: {max_:,d}"
        ),
    )
    plt.xAxis.name = "Read length / kb"
    plt.yAxis.name = "Number of reads"

    if xlim[0] is not None:
        plt.xAxis.min = xlim[0] / 1000
    if xlim[1] is not None:
        plt.xAxis.max = xlim[1] / 1000
    return plt


def load_fastcat(fpath, target_cols=None):
    """Load and prepare fastcat per-read stats.

    :param fpath: path to a fastcat stats file.
    :target_cols: columns to be loaded in the dataframe.

    :returns: a dataframe
    """
    cols, time_cols = _intersect_columns(copy.copy(FASTCAT_COLS_DTYPES), target_cols)
    try:
        df = pd.read_csv(
            fpath, sep="\t", usecols=cols.keys(), dtype=cols, parse_dates=time_cols
        )
    except pd.errors.EmptyDataError:
        raise Exception(f"Empty input: {fpath}")
    df = _localize_time(df)
    return df


def load_bamstats(fpath, target_cols=None):
    """Load and prepare bamstats per-read stats.

    :param fpath: path to a bamstats stats file.
    :target_cols: columns to be loaded in the dataframe.

    :returns: a dataframe
    """
    cols, time_cols = _intersect_columns(copy.copy(BAMSTATS_COLS_DTYPES), target_cols)
    try:
        df = pd.read_csv(
            fpath, sep="\t", usecols=cols.keys(), dtype=cols, parse_dates=time_cols
        )
    except pd.errors.EmptyDataError:
        raise Exception(f"Empty input: {fpath}")
    df = _localize_time(df)
    # to be consistent with fastcat
    df.rename(columns={"name": "read_id"}, inplace=True)
    return df


def load_bamstats_flagstat(fpath):
    """Load and prepare bamstats flagstat output.

    :param fpath: path to a bamstats flagstat file.

    :returns: a dataframe
    """
    try:
        df = pd.read_csv(
            fpath,
            sep="\t",
            usecols=BAMSTATS_FLAGSTAT_COLS_DTYPES.keys(),
            dtype=BAMSTATS_FLAGSTAT_COLS_DTYPES,
        )
    except pd.errors.EmptyDataError:
        raise Exception(f"Empty input: {fpath}")
    df["status"] = df["ref"].apply(lambda x: "Unmapped" if x == "*" else "Mapped")
    return df


def load_histogram(hist_dir, dtype="quality"):
    """Load fastcat/bamstats histograms.

    :param hist_dir: pathname to input directory.
    :param dtype: histogram datatype to load.
    """
    allowed = {
        "quality",
        "length",
        "quality.unmap",
        "length.unmap",
        "accuracy",
        "coverage",
    }
    if dtype not in allowed:
        raise ValueError(f"`dtype` must be one of {allowed}.")
    dt = float
    if "length" in dtype:
        dt = int

    hist = pd.read_csv(
        os.path.join(hist_dir, f"{dtype}.hist"),
        sep="\t",
        names=["start", "end", "count"],
        dtype={"start": dt, "end": dt, "count": int},
    )
    return hist


def load_stats(fpath, target_cols=None):
    """Load and prepare fastcat or bamstats per-read stats.

    This function is intended to be used when the caller does not know (and care)
    the origin of the input file, but wishes to load the common columns.

    :params fpath: path to a fastcat or bamstats stats file.
    :param target_cols: list of columns to read from file.

    :returns: a dataframe
    """
    if target_cols is None:
        target_cols = ["sample_name", "read_length", "mean_quality"]
    df = None
    try:
        df = load_fastcat(fpath, target_cols=target_cols)
    except ValueError:
        df = load_bamstats(fpath, target_cols=target_cols)
    return df


def histogram_median(hist, x="start", y="count"):
    """Calculate the median value from histogram data.

    :param hist: pd.DataFrame with columns [start, end, count].
    :param x: the x-axis variable.
    :param y: the y-axis variable.
    """
    # TODO: start and end may not be end = start + 1
    cumsum = np.cumsum(hist[y]).to_numpy()
    mid = cumsum[-1] / 2
    pos = np.searchsorted(cumsum, mid)
    return hist[x][pos]


def main(args):
    """Entry point to demonstrate a sequence summary component."""
    comp_title = "Sequence Summary"
    # Define inputs.
    # If seq_summary is not passed, then use bam_readstats
    if args.seq_summary:
        seq_summary = args.seq_summary
    elif args.seq_summary is None and args.bam_readstats is not None:
        seq_summary = args.bam_readstats
    else:
        raise ValueError("No valid input for seq_summary/bam_readstats.")
    # Create summary
    seq_sum = SeqSummary(seq_summary, flagstat=args.bam_flagstat)
    # Write report
    report = ComponentReport(comp_title, seq_sum)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        "Sequence summary",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False,
    )
    parser.add_argument(
        "--seq_summary",
        default=resource_filename("ezcharts", "data/test/fastcat"),
        help="Sequence summary TSV from fastcat.",
    )
    parser.add_argument(
        "--bam_flagstat",
        default=resource_filename(
            "ezcharts", "data/test/bamstats/bamstats.flagstat.tsv"
        ),
        help="Bam flagstats TSV from bamstats.",
    )
    parser.add_argument(
        "--bam_readstats",
        default=resource_filename("ezcharts", "data/test/bamstats/"),
        help="Read statistics TSV from bamstats.",
    )
    parser.add_argument(
        "--output", default="seq_summary_report.html", help="Output HTML file."
    )
    return parser
