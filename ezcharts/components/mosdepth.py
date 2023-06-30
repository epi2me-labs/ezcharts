"""An ezcharts component for loading mosdepth data."""
import argparse
import os

import pandas as pd
from pandas.api import types as pd_types
from pkg_resources import resource_filename

from ezcharts.components.common import add_missing_windows, fasta_idx
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import DataTable, Tabs
from ezcharts.plots.relational import lineplot

# Categorical types
CATEGORICAL = pd_types.CategoricalDtype(ordered=True)


class DepthSummary(Snippet):
    """Generate modified bases summary plots."""

    def __init__(self, theme='epi2melabs', **kwargs):
        """Create depth summary componet.

        If dml/dmr contains results from multiple samples, each will be
        plotted in its own tab.

        :param mosdepth_summary: A path to a mosdepth summary output file or
            DataFrame
        :param mosdepth_region: A path to a mosdepth region output file or
            DataFrame
        :param faidx: A path to a fasta fai index or
            DataFrame
        """
        super().__init__(styles=None, classes=None)

        with self:
            if 'faidx' in kwargs:
                if isinstance(kwargs['faidx'], pd.DataFrame):
                    faidx = kwargs['faidx']
                elif isinstance(kwargs['faidx'], str):
                    faidx = fasta_idx(kwargs['faidx'])
                else:
                    faidx = None

            # Make modkit summary table
            if "mosdepth_summary" in kwargs:
                if isinstance(kwargs["mosdepth_summary"], pd.DataFrame):
                    summary = kwargs["mosdepth_summary"]
                else:
                    summary = load_mosdepth_summary(kwargs["mosdepth_summary"])
                # Check that the file is not empty
                if summary[0].empty:
                    raise pd.errors.EmptyDataError('Summary is empty')
                # the following assumes that `fastcat` / `bamstats` has been run
                # with `-s` which is not necessarily the case (if there was only
                # one sample) --> create a dummy 'sample_name' column if missing
                if 'sample_name' not in summary[0].columns:
                    summary[0]['sample_name'] = 'sample'
                    summary[1]['sample_name'] = 'sample'
                # If one sample, save one plot
                if len(summary[0]['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    DataTable.from_pandas(summary[0], use_index=False)
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in summary[0].groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                DataTable.from_pandas(df_sample, use_index=False)

            # Make mosdepth line plot
            if "mosdepth_region" in kwargs:
                if isinstance(kwargs["mosdepth_region"], pd.DataFrame):
                    bed = kwargs["mosdepth_region"]
                else:
                    bed = load_mosdepth_regions(
                        kwargs["mosdepth_region"], faidx=faidx,
                        winsize=25000, min_size=10000000)
                # Check that the file is not empty
                if bed.empty:
                    raise pd.errors.EmptyDataError('Region DF is empty')
                # the following assumes that `fastcat` / `bamstats` has been run
                # with `-s` which is not necessarily the case (if there was only
                # one sample) --> create a dummy 'sample_name' column if missing
                if 'sample_name' not in bed.columns:
                    bed['sample_name'] = 'sample'
                # If one sample, save one plot
                if len(bed['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    plt = lineplot(
                        data=bed, x='total_mean_pos',
                        y='depth', hue='chrom')
                    # Remove markers
                    for s in plt.series:
                        s.showSymbol = False
                    EZChart(plt, 'epi2melabs')
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in bed.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                # we only got a single sample --> no dropdown
                                plt = lineplot(
                                    data=df_sample, x='total_mean_pos',
                                    y='depth', hue='chrom')
                                # Remove markers
                                for s in plt.series:
                                    s.showSymbol = False
                                EZChart(plt, 'epi2melabs')


# Load region mosdepth output file
def load_mosdepth_regions(
        mosdepth, faidx=None, subset=None,
        karyo=None, winsize=25000, min_size=0):
    """Load mosdepth results into dataframe.

    Input is either a single directory with all the mosdepth outputs or
    a single mosdepth file.

    Optional inputs can be:
    - faidx: A faidx dataframe with 'chrom' 'length' cols (add missing intervals)
    - winsize: A window size (int, needed to add back missing intervals)
    - karyo: A ordered karyotype (dictionary of "chrom" : int(position), e.g.
    {'chr1': 1, ..., 'chrY': 24})
    - subset: A subset of sequences to use as a list
    """
    relevant_stats_cols_dtypes = {
        "chrom": CATEGORICAL,
        "start": int,
        "end": int,
        "depth": float,
    }
    # Check inputs
    dfs = []
    if os.path.isdir(mosdepth):
        input_files = [(mosdepth, i) for i in os.listdir(mosdepth)]
    elif os.path.isfile(mosdepth):
        input_files = [(None, mosdepth)]
    else:
        raise Exception(f'No valid input: {mosdepth}')
    # If no files, raise error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {mosdepth}')
    # Process each file
    for (inpath, fname) in input_files:
        try:
            # Define file name
            mosdepth_file = fname if not inpath else f'{inpath}/{fname}'
            # Load input
            df = pd.read_csv(
                mosdepth_file,
                sep="\t",
                names=relevant_stats_cols_dtypes.keys(),
                dtype=relevant_stats_cols_dtypes
            )
            # If it's empty, add an empty DF
            if df.empty:
                cols = relevant_stats_cols_dtypes.update(
                    {
                        'mean_pos': int, 'step': int,
                        "total_mean_pos": int, "filename": str})
                dfs.append(pd.DataFrame(columns=cols))
                continue
            # If chrom sizes are provided, add missing windows in each chrom
            if isinstance(faidx, pd.DataFrame) and isinstance(winsize, int):
                if 'length' not in faidx.columns:
                    raise ValueError(
                        'No "length" column found.',
                        'Import the fai with fasta_idx() and try again.')
                if 'chrom' not in faidx.columns:
                    raise ValueError(
                        'No "chrom" column found.',
                        'Import the fai with fasta_idx() and try again.')
                faidx = faidx.loc[faidx['length'] > min_size]
                df = add_missing_windows(df, faidx, value='depth', winsize=winsize)
            # If karyo provided, sort by given order
            df = (
                df.eval("mean_pos = (start + end) / 2")
                .eval("step = end - start")
                .reset_index(drop=True)
                )
            if subset:
                subset = subset if isinstance(subset, list) else [subset]
                df = df.loc[df['chrom'].isin(subset)]
            if karyo:
                # Sort column by chromosome number
                df = df.eval("chr_id = chrom.map(@karyo)") \
                    .sort_values(["chr_id", "start"]) \
                    .drop(columns="chr_id")
            # Remove and reorder categories
            df['chrom'] = \
                df.chrom.cat.remove_unused_categories()
            df['chrom'] = \
                df.chrom.cat.reorder_categories(
                [i for i in df.chrom.unique()])

            # If faidx is provided, use that to compute the cumulative positions
            if isinstance(faidx, pd.DataFrame):
                ref_lengths = faidx.groupby(
                    "chrom", observed=True, sort=False)["length"].last()
                total_ref_starts = ref_lengths.cumsum().shift(1, fill_value=0)
            # Otherwise, use the df
            else:
                ref_lengths = df.groupby(
                    "chrom", observed=True, sort=False)["end"].last()
                total_ref_starts = ref_lengths.cumsum().shift(1, fill_value=0)

            # Add cumulative depth
            df["total_mean_pos"] = df.apply(
                lambda x: x.mean_pos + total_ref_starts[x.chrom], axis=1)
            # Add filename
            df['filename'] = fname.split('/')[-1]
            # Add to list
            dfs.append(df)
        except pd.errors.EmptyDataError:
            cols = relevant_stats_cols_dtypes.update({'filename': str})
            dfs.append(pd.DataFrame(columns=cols)) \
                .astype({"chrom": CATEGORICAL})
    return pd.concat(dfs).reset_index(drop=True)


def load_mosdepth_summary(summary):
    """Load mosdepth results into dataframe."""
    relevant_stats_cols_dtypes = {
        "chrom": CATEGORICAL,
        "length": int,
        "bases": int,
        "mean": float,
        "min": int,
        "max": int
    }
    # Check inputs
    dfs_tot = []
    dfs_reg = []
    if os.path.isdir(summary):
        input_files = [(summary, i) for i in os.listdir(summary)]
    elif os.path.isfile(summary):
        input_files = [(None, summary)]
    else:
        raise Exception(f'No valid input: {summary}')
    # If no files, raise error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {summary}')
    # Process each file
    for (inpath, fname) in input_files:
        try:
            # Define file name
            summary_file = fname if not inpath else f'{inpath}/{fname}'
            # Load input
            df = pd.read_csv(
                summary_file,
                sep="\t",
                usecols=relevant_stats_cols_dtypes.keys(),
                dtype=relevant_stats_cols_dtypes
                )
            # If it's empty, add an empty DF
            if df.empty:
                cols = relevant_stats_cols_dtypes.update(
                    {'filename': str})
                dfs_tot.append(pd.DataFrame(columns=cols))
                dfs_reg.append(pd.DataFrame(columns=cols))
                continue
            # Add filename
            df['filename'] = fname.split('/')[-1]
            # Split region/total stats
            dfs_tot.append(df[~df['chrom'].str.contains("_region")])
            dfs_reg.append(df[df['chrom'].str.contains("_region")])

        # Empty data error > append empty DF with the right structure
        except pd.errors.EmptyDataError:
            cols = relevant_stats_cols_dtypes.update({'filename': str})
            dfs_tot.append(pd.DataFrame(columns=cols))
            dfs_reg.append(pd.DataFrame(columns=cols))
    return (
        pd.concat(dfs_tot).reset_index(drop=True),
        pd.concat(dfs_reg).reset_index(drop=True))


def main(args):
    """Entry point to demonstrate a depth component."""
    comp_title = 'Mosdepth results'
    seq_sum = DepthSummary(
        mosdepth_summary=args.mosdepth_summary,
        mosdepth_region=args.mosdepth_region,
        faidx=args.faidx
        )
    report = ComponentReport(comp_title, seq_sum)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'Modkit summary',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--mosdepth_summary",
        default=resource_filename('ezcharts', "data/test/test_mosdepth_summary.tsv"),
        help="Resulting summary file from mosdepth.")
    parser.add_argument(
        "--mosdepth_region",
        default=resource_filename('ezcharts', "data/test/test_mosdepth.bed.gz"),
        help="Resulting region coverage bed file from mosdepth.")
    parser.add_argument(
        "--faidx",
        default=resource_filename('ezcharts', "data/test/ref.fa.fai"),
        help="Reference fasta fai file.")
    parser.add_argument(
        "--output",
        default="mosdepth_report.html",
        help="Output HTML file.")
    return parser
