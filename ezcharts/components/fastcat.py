"""An ezcharts component for plotting sequence summaries."""
import argparse
import copy
import os

from bokeh.models import Title
import numpy as np
import pandas as pd
from pkg_resources import resource_filename
import sigfig

import ezcharts as ezc
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import DataTable, Grid, Tabs
from ezcharts.plots import BokehPlot, util
from ezcharts.plots.util import empty_plot


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
        seq_summary=None,
        flagstat=None,
        sample_names=None,
        theme="epi2melabs",
        color=None,
        height="500px",
        alignment_stats=True,
        # [CW-5211]
        # When users are sequencing small molecules they sometimes find
        # spurious "long" reads which are either real concatemers or artefacts
        # these have the effect of causing aggressive binning in the read length
        # plot such that any detail is lost from the main distribution.
        # This arg allows the binwidth of the length plot to be customised to
        # customer requirements.
        read_length_plot_binwidth=None,
        # [CW-5562]
        # Set an initial quantile x-axis max in the length plot so that long
        # read outliers are not visible. If None, all data is shown.
        read_length_quantile_xend=None
    ):
        """Create sequence summary component.

        :param seq_summary: a path to a fastcat/bamstats read stats output file
            or dataframe (or a tuple of such).
        :param flagstat: a path to a bamstats flagstat output file or dataframe
            (or tuple of such).
        :sample_names: tuple of sample names. Required when other input arguments
            are tuples.
        :param theme: String defining the visual theme for the plots.
        :param color: String defining the color for the plots.
        :param height: String defining the height of the plots.
        :param alignment_stats: Boolean defining whether to display the alignments
         stats.
        :param read_length_plot_binwidth: int bin widths for read length plot.
        :param read_length_quantile_xend: float quantile range end for x-axis length
         plot

        """
        super().__init__(styles=None, classes=None)
        self.theme = theme
        self.color = color
        self.read_length_plot_binwidth = read_length_plot_binwidth
        self.read_length_quantile_xend = read_length_quantile_xend

        # we need at least seq_summary or histograms
        if seq_summary is None:
            raise ValueError("One of `seq_summary` must be provided.")
        if not (
            isinstance(seq_summary, pd.DataFrame)
            or isinstance(seq_summary, str)
            or isinstance(seq_summary, tuple)
        ):
            raise ValueError(
                "`seq_summary` must be a path to a fastcat/bamstats read stats output "
                "file or dataframe (or a tuple of such)."
            )

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
                    for sample_name, data in sorted(
                        zip(sample_names, seq_summary), key=lambda x: x[0]
                    ):
                        with tabs.add_dropdown_tab(sample_name):
                            ldata, qdata, adata, cdata = self._load_summary_data(data)
                            self._draw_summary_plots(ldata, qdata, height)
                            if alignment_stats:
                                self._draw_alignment_plots(adata, cdata, height)
            else:
                # single sample
                ldata, qdata, adata, cdata = self._load_summary_data(seq_summary)
                self._draw_summary_plots(ldata, qdata, height)
                if alignment_stats:
                    self._draw_alignment_plots(adata, cdata, height)

            # same again for flagstat
            if flagstat is not None:
                if isinstance(flagstat, tuple):
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_name, data in sorted(
                            zip(sample_names, flagstat), key=lambda x: x[0]
                        ):
                            with tabs.add_dropdown_tab(sample_name):
                                self._draw_bamstat_table(data)
                else:
                    self._draw_bamstat_table(flagstat)

    def _load_summary_data(
        self,
        data
    ):
        """Draw quality, read_length, yield, accuracy and coverage plots using raw data.

        :param seq_summary: pd.DataFrame containing per-sequence summary information.
        :param theme: EPI2ME theme.
        """
        # data is either a summary file, a dataframe (of a summary file),
        # or a directory (of histogram files).
        adata, cdata, qdata, ldata = None, None, None, None
        if isinstance(data, pd.DataFrame):
            qdata, ldata = data, data
            adata = data if 'acc' in data.columns else None
            cdata = data if 'coverage' in data.columns else None
        else:
            try:
                df = load_stats(data)
                qdata, ldata = df, df
                adata = df if 'acc' in df.columns else None
                cdata = df if 'coverage' in df.columns else None
            except Exception:
                try:
                    qdata = load_histogram(data, "quality")
                    ldata = load_histogram(data, "length")
                    # Try loading BAMstats files
                    try:
                        adata = load_histogram(data, "accuracy")
                        cdata = load_histogram(data, "coverage")
                    except Exception:
                        adata, cdata = None, None
                    # Try loading unmapped files
                    try:
                        qdata = sum_hists((
                            qdata,
                            load_histogram(data, "quality.unmap")
                        ))
                        ldata = sum_hists((
                            ldata,
                            load_histogram(data, "length.unmap")
                        ))
                    except Exception:
                        qdata, ldata

                except Exception:
                    raise ValueError("Could not load input data.")
        return ldata, qdata, adata, cdata

    def _draw_summary_plots(
        self,
        ldata,
        qdata,
        height,
    ):
        """Draw quality, read_length and yield plots using raw data.

        :param ldata: pd.DataFrame containing length values.
        :param qdata: pd.DataFrame containing quality values.
        :param color: color for the plots.
        :param height: height of the plot
        """
        with Grid(columns=3):
            if not qdata.empty:
                EZChart(
                    read_quality_plot(qdata, color=self.color),
                    self.theme,
                    height=height,
                )
            else:
                EZChart(empty_plot())
            if not ldata.empty:
                len_args = {}
                if self.read_length_quantile_xend:
                    len_args['quantile_limits'] = True
                    len_args['xlim'] = (0, self.read_length_quantile_xend)
                EZChart(
                    read_length_plot(
                        ldata, color=self.color,
                        binwidth=self.read_length_plot_binwidth, **len_args),
                    self.theme,
                    height=height,
                )
                EZChart(
                    base_yield_plot(ldata, color=self.color), self.theme, height=height)
            else:
                EZChart(empty_plot())
                EZChart(empty_plot())

    def _draw_alignment_plots(
        self,
        adata,
        cdata,
        height,
    ):
        """Draw accuracy and coverage plots using raw data.

        :param adata: pd.DataFrame containing accuracy values.
        :param cdata: pd.DataFrame containing coverage values.
        """
        if adata is not None or cdata is not None:
            with Grid(columns=2):
                if adata is not None:
                    try:
                        EZChart(
                            mapping_accuracy_plot(adata, color=self.color),
                            self.theme, height=height)
                    except Exception:
                        pass
                if cdata is not None:
                    try:
                        EZChart(
                            read_coverage_plot(cdata, color=self.color),
                            self.theme, height=height)
                    except Exception:
                        pass

    def _draw_bamstat_table(self, data):
        if not isinstance(data, pd.DataFrame):
            data = load_bamstats_flagstat(data)
        DataTable.from_pandas(data, use_index=False)


class SeqCompare(Snippet):
    """Generate sequence comparison plots."""

    def __init__(
        self,
        seq_summary=None,
        flagstat=None,
        sample_names=None,
        theme="epi2melabs",
        color=None,
        height="500px",
        alignment_stats=True,
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
        self.color = color
        self.alignment_stats = alignment_stats
        self.metrics = [
            'length',
            'yield',
            'quality',
            'accuracy',
            'coverage'
        ]
        self.columns = [
            'read_length',
            'read_length',
            'mean_quality',
            'acc',
            'coverage'
        ]
        self.plot_functions = [
            read_length_plot,
            base_yield_plot,
            read_quality_plot,
            mapping_accuracy_plot,
            read_coverage_plot
        ]

        # we need at least seq_summary or histograms
        if seq_summary is None:
            raise ValueError("One of `seq_summary` must be provided.")
        if not (
            isinstance(seq_summary, pd.DataFrame)
            or isinstance(seq_summary, str)
            or isinstance(seq_summary, tuple)
        ):
            raise ValueError(
                "`seq_summary` must be a path to a fastcat/bamstats read stats output "
                "file or dataframe (or a tuple of such)."
            )

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
                self._compare_summary_plots(
                    sample_names, seq_summary, height=height)
            else:
                # single sample
                self._compare_summary_plots(
                    tuple('Sample'), tuple(seq_summary), height=height)

            # same again for flagstat
            if flagstat is not None:
                if isinstance(flagstat, tuple):
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_name, data in sorted(
                            zip(sample_names, flagstat), key=lambda x: x[0]
                        ):
                            with tabs.add_dropdown_tab(sample_name):
                                self._draw_bamstat_table(data)
                else:
                    self._draw_bamstat_table(flagstat)

    def _compare_summary_plots(self, samples, datasets, height):
        """Draw quality, read_length, yield, accuracy and coverage plots using raw data.

        :param samples: tuple of sample names to process.
        :param datasets: data to process, in the same order as the samples.
        """
        # data is either a summary file, a dataframe (of a summary file),
        # or a directory (of histogram files).
        qdata, ldata = [], []
        all_plots = {
            'length': [],
            'yield': [],
            'quality': [],
            'accuracy': [],
            'coverage': []

        }
        # For each metric and each sample, create the plot
        if not isinstance(datasets, tuple):
            raise ValueError(
                "SeqSummary by `metric` only Tuples as input."
            )
        else:
            # TODO: test with one DF directly
            if isinstance(datasets, pd.DataFrame):
                for (metric, col, plot_function) in zip(
                        self.metrics, self.columns, self.plot_functions):
                    if col in datasets.columns:
                        all_plots[metric] += [plot_function(datasets, color=self.color)]
                    else:
                        all_plots[metric] += [None]
            for (sample, data) in zip(samples, datasets):
                try:
                    df = load_stats(data)
                    for (metric, col, plot_function) in zip(
                            self.metrics, self.columns, self.plot_functions):
                        if col in df.columns:
                            all_plots[metric] += [plot_function(df, color=self.color)]
                        else:
                            all_plots[metric] += [None]

                except Exception:
                    # Bare minimum, should always be there
                    try:
                        qdata = load_histogram(data, "quality")
                        ldata = load_histogram(data, "length")
                    except Exception:
                        raise ValueError("Could not load input data.")
                    # Try loading and adding unmapped hists, if available
                    try:
                        qdata = sum_hists((
                            load_histogram(data, "quality"),
                            load_histogram(data, "quality.unmap")
                        ))
                        ldata = sum_hists((
                            load_histogram(data, "length"),
                            load_histogram(data, "length.unmap")
                        ))
                    except Exception:
                        qdata, ldata
                    if not ldata.empty:
                        all_plots["length"] += [
                            read_length_plot(ldata, color=self.color)
                        ]
                        all_plots["yield"] += [base_yield_plot(ldata, color=self.color)]
                    else:
                        all_plots["length"] += [empty_plot()]
                        all_plots["yield"] += [empty_plot()]
                    if not qdata.empty:
                        all_plots["quality"] += [
                            read_quality_plot(qdata, color=self.color)
                        ]
                    else:
                        all_plots["quality"] += [empty_plot()]
                    # Try loading BAMstats-specific hists and add their plots, if needed
                    if self.alignment_stats:
                        try:
                            all_plots['accuracy'] += [
                                mapping_accuracy_plot(
                                    load_histogram(data, "accuracy"),
                                    color=self.color
                                )
                            ]
                        except Exception:
                            all_plots['accuracy'] += [None]
                        try:
                            all_plots['coverage'] += [
                                read_coverage_plot(
                                    load_histogram(data, "coverage"),
                                    color=self.color
                                )
                            ]
                        except Exception:
                            all_plots['coverage'] += [None]

        # Create tabs
        tabs = Tabs()
        for metric in self.metrics:
            pairs = [(p, s) for p, s in zip(all_plots[metric], samples) if p]
            if len(pairs) == 0:
                continue
            with tabs.add_tab(metric):
                with Grid(columns=min(len(pairs), 3)):
                    plots, samps = zip(*sorted(pairs, key=lambda x: x[1]))
                    self._coordinate_plots(plots, labels=samps)
                    for plot in plots:
                        EZChart(plot, self.theme, height=height)

    def _is_empty_plot(self, plot):
        """Check if the plot is empty."""
        if not plot:
            return True
        if isinstance(plot, BokehPlot):
            if "_fig" not in dir(plot):
                return True
            for renderer in plot._fig.renderers:
                if not hasattr(renderer, 'glyph'):
                    return True
        else:
            if not plot.dataset:
                return True
        return False

    def _coordinate_plots(self, plots, labels=None):
        """Coordinate the axes between the plots."""
        max_by_plot = []
        for plot in plots:
            if not self._is_empty_plot(plot):
                if isinstance(plot, BokehPlot):
                    dimensions = plot._fig.renderers[0].data_source.to_df()
                    if 'top' in dimensions.columns:
                        col = 'top'
                    else:
                        col = 'y'
                    y_val = dimensions[col].max()
                else:
                    dimensions = np.array(plot.dataset[0].dimensions)
                    if 'y' in dimensions:
                        y_col = np.where(dimensions == 'y')[0]
                    else:
                        y_col = np.where(dimensions == 'height')[0]
                    y_val = np.max(plot.dataset[0].source, axis=0)[y_col]
                max_by_plot.append(y_val)
        # Set new values
        if labels:
            inputs = zip(plots, labels)
        else:
            inputs = zip(plots, [None] * len(plots))
        for (plot, label) in inputs:
            if not self._is_empty_plot(plot):
                plot._fig.y_range.end = max(max_by_plot)
                if label:
                    plot._fig.add_layout(
                        Title(text=label, text_font_size="1.5em"), 'above')
            else:
                if label:
                    plot.title.text = label

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
    n50 = int(length[n50_index])
    # TODO: we needn't create this only to thin it immediately
    df = pd.DataFrame({xlab: length / 1000, ylab: cumsum / 1e9}, copy=False)

    # thin the data while keeping last
    if len(df) > thinning:
        step = len(df) // thinning
        df = pd.concat((df.loc[::step, :], df.iloc[[-1]]), axis=0)

    plt = ezc.lineplot(data=df, x=xlab, y=ylab, hue=None, color=color, marker=False)
    subtext = (
        f"Total yield: {sigfig.round(df.iloc[0][ylab], sigfigs=3)} Gb. "
        f" N50: {sigfig.round(n50, 3)}kb")

    plt._fig.add_layout(Title(text=subtext, text_font_size="0.8em"), 'above')
    plt._fig.add_layout(
        Title(text="Base yield above read length", text_font_size="1.5em"), 'above')
    return plt


@ezc.plots.util.plot_wrapper
def histogram_plot(
    data, col="count", binwidth=None, min_val=None,
    max_val=None, title="Histogram",
    xaxis_label=None, color=None
):
    """Create histogram summary plot.

    :param data: fastcat/bamstats summary data or read-length histogram data.
    :param binwidth: width of each bin.
    :param min_val: the minimum value to plot.
    :param max_val: the maximum value to plot.
    :param title: title of the plot.
    """
    plt, mean_val, median_val = None, None, None
    if "read_length" in data.columns:
        # When min_val==0, "if not min_val" evaluates to True.
        # Instead use "if min_val is None"
        if min_val is None:
            min_val = data[col].min()
        if max_val is None:
            max_val = data[col].max() + binwidth
        # fastcat/bamstats
        mean_val = np.round(data[col].mean(), 1)
        median_val = data[col].median()
        plt = ezc.histplot(
            data=data[col], binwidth=binwidth, binrange=(min_val, max_val), color=color
        )
    else:
        if min_val is None:
            min_val = data.end.min()
        if max_val is None:
            max_val = data.end.max() + binwidth
        # histogram
        mean_val = np.round(
            np.average(0.5 * (data["start"] + data["end"]), weights=data["count"]), 1
        )
        median_val = int(histogram_median(data))
        plt = ezc.histplot(
            data=data["start"],
            weights=data["count"],
            binwidth=binwidth,
            binrange=(min_val, max_val),
            color=color
        )

    subtitle = f"Mean: {mean_val:.1f}. Median: {median_val:.1f}"

    if xaxis_label:
        plt._fig.xaxis.axis_label = xaxis_label
    plt._fig.add_layout(Title(text=subtitle, text_font_size="0.8em"), 'above')
    plt._fig.add_layout(Title(text=title, text_font_size="1.5em"), 'above')
    plt._fig.x_range.start, plt._fig.x_range.end = min_val, max_val
    plt._fig.yaxis.axis_label = "Number of reads"
    return plt


@ezc.plots.util.plot_wrapper
def read_quality_plot(data, binwidth=0.2, min_qual=4, max_qual=30, color=None):
    """Create read quality summary plot.

    :param data: fastcat/bamstats summary data or read-length histogram data.
    :param binwidth: width of each bin.
    :param min_qual: the minimum quality value to plot.
    :param max_qual: the maximum quality value to plot.
    """
    plt = histogram_plot(
        data, col='mean_quality', binwidth=binwidth, min_val=min_qual,
        max_val=max_qual, title="Read quality",
        xaxis_label="Quality", color=color
    )
    return plt


@ezc.plots.util.plot_wrapper
def mapping_accuracy_plot(
    data, binwidth=1.0, min_acc=80,
    max_acc=101, color=None
):
    """Create read quality summary plot.

    :param data: fastcat/bamstats summary data or read-length histogram data.
    :param binwidth: width of each bin.
    :param min_acc: the minimum quality value to plot.
    :param max_acc: the maximum quality value to plot.
    """
    data = data[data['acc'].notna()]
    if len(data) == 0:
        plt = util.empty_plot(
            text="Accuracy",
            subtext="No aligned reads to plot.")
    else:
        plt = histogram_plot(
            data, col='acc', binwidth=0.2, min_val=min_acc,
            max_val=max_acc, title="Accuracy",
            xaxis_label="Accuracy", color=color
        )
    return plt


@ezc.plots.util.plot_wrapper
def read_coverage_plot(
    data, binwidth=1.0, min_cov=0,
    max_cov=None, color=None
):
    """Create read quality summary plot.

    :param data: fastcat/bamstats summary data or read-length histogram data.
    :param binwidth: width of each bin.
    :param min_cov: the minimum coverage value to plot.
    :param max_cov: the maximum coverage value to plot.
    """
    data = data[data['coverage'].notna()]
    if len(data) == 0:
        plt = util.empty_plot(
            text="Read alignment",
            subtext="No aligned reads to plot.")
    else:
        plt = histogram_plot(
            data, col='coverage', binwidth=0.2, min_val=min_cov,
            max_val=max_cov, title="Read alignment",
            xaxis_label="Percentage of read aligned", color=color
        )
    return plt


@ezc.plots.util.plot_wrapper
def read_length_plot(
    data, xlim=(0, None), quantile_limits=False,
    bins=100, binwidth=None, title="Read length", color=None
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
        weights = None
    else:
        # histogram
        if max_len is None:
            max_len = data.iloc[-1]["end"]
        if quantile_limits:
            cs_counts = np.cumsum(data["count"])
            total_counts = cs_counts.iloc[-1]
            top_value = xlim[1] * total_counts
            top_index = np.searchsorted(cs_counts, top_value)
            bottom_value = xlim[0] * total_counts
            bottom_idx = np.searchsorted(cs_counts, bottom_value)
            min_len = data.iloc[bottom_idx].start
            max_len = data.iloc[top_index].start
            xlim = (min_len, max_len)

        median_length = histogram_median(data)
        mean_length = np.average(data["start"], weights=data["count"])
        max_ = data.iloc[-1]["start"]
        min_ = data.iloc[0]["start"]
        weights = data["count"]
        read_lengths = data['start']

    if quantile_limits and binwidth is None:
        # Set number of bins such that the initial quantile-trimmed view has the desired
        # number of bins.
        bins = int(bins * read_lengths.max() / max_len)

    if binwidth is not None:
        binwidth /= 1000

    read_lengths = read_lengths / 1000
    plt = ezc.histplot(
        read_lengths,
        bins=bins,
        binwidth=binwidth,
        weights=weights,
        color=color
    )
    # customize the plot
    plt._fig.xaxis.axis_label = "Read length / kb"
    plt._fig.yaxis.axis_label = "Number of reads"
    subtext = (
        f"Mean: {mean_length:.1f}. Median: {median_length:.1f}. "
        f"Min: {min_:,d}. Max: {max_:,d}"
    )
    plt._fig.add_layout(Title(text=subtext, text_font_size="0.8em"), 'above')
    plt._fig.add_layout(Title(text=title, text_font_size="1.5em"), 'above')

    if xlim[0] is not None:
        plt._fig.x_range.start = xlim[0] / 1000
    if xlim[1] is not None:
        plt._fig.x_range.end = xlim[1] / 1000
    return plt


def sum_hists(hists):
    """Sum two histogram dataframes based on the intervals."""
    if not isinstance(hists, tuple):
        raise ValueError("Input is not a tuple of dataframes.")
    return pd.concat(
        hists
    )\
        .reset_index(drop=True)\
        .sort_values(by='start')\
        .groupby(['start', 'end'])\
        .sum().reset_index()


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
    target_cols_fastcat, target_cols_bamstats = target_cols, target_cols
    if target_cols is None:
        target_cols_fastcat = ["sample_name", "read_length", "mean_quality"]
        target_cols_bamstats = [
            "sample_name", "read_length", "mean_quality", "acc", "coverage"]
    df = None
    try:
        df = load_bamstats(fpath, target_cols=target_cols_bamstats)
    except ValueError:
        df = load_fastcat(fpath, target_cols=target_cols_fastcat)
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
        raise ValueError('No valid input for seq_summary/bam_readstats.')
    bam_flagstat = tuple(args.bam_flagstat) \
        if isinstance(args.bam_flagstat, list) \
        else args.bam_flagstat
    sample = tuple(args.sample) \
        if isinstance(args.sample, list) \
        else args.sample
    # Create summary
    if args.by == 'sample':
        seq_sum = SeqSummary(
            tuple(seq_summary),
            flagstat=bam_flagstat,
            sample_names=sample,
            alignment_stats=False if args.skip_alignment_stats else True,
            color=args.color,
        )
    else:
        seq_sum = SeqCompare(
            tuple(seq_summary),
            flagstat=bam_flagstat,
            sample_names=sample,
            alignment_stats=False if args.skip_alignment_stats else True,
            color=args.color,
        )

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
        nargs='+'
    )
    parser.add_argument(
        "--bam_flagstat",
        default=resource_filename(
            "ezcharts", "data/test/bamstats/bamstats.flagstat.tsv"
        ),
        help="Bam flagstats TSV from bamstats.",
        nargs='+'
    )
    parser.add_argument(
        "--sample",
        default='sample',
        help="Sample name.",
        nargs='+'
    )
    parser.add_argument(
        "--by",
        default='sample',
        choices=['sample', 'metric'],
        help="Create SeqSummary by sample or by metric.",
    )
    parser.add_argument(
        "--bam_readstats",
        default=resource_filename("ezcharts", "data/test/bamstats/"),
        help="Read statistics TSV from bamstats.",
        nargs='+'
    )
    parser.add_argument(
        "--skip_alignment_stats",
        action="store_true",
        help="Skip alignment statistics histograms (coverage and accuracy)."
    )
    parser.add_argument(
        "--color",
        help="Plot color."
    )
    parser.add_argument(
        "--output", default="seq_summary_report.html", help="Output HTML file."
    )
    return parser
