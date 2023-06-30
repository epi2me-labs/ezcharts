"""An ezcharts component for loading data from DSS R package.

[DSS](https://bioconductor.org/packages/release/bioc/vignettes/DSS/inst/doc/DSS.html)
"""
import argparse
import os

import pandas as pd
from pandas.api import types as pd_types
from pkg_resources import resource_filename

from ezcharts.components.common import fasta_idx
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import Tabs
from ezcharts.plots.karyomap import karyomap

# Categorical types
CATEGORICAL = pd_types.CategoricalDtype(ordered=True)


class DMSummary(Snippet):
    """Generate differentially modified plots."""

    def __init__(self, theme='epi2melabs', **kwargs):
        """Create depth summary componet.

        If dml/dmr contains results from multiple samples, each will be
        plotted in its own tab.

        :param dml: A path to a DSS differentially modified loci file or
            DataFrame
        :param dmr: A path to a DSS differentially modified regions file or
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
            if "dml" in kwargs:
                if isinstance(kwargs["dml"], pd.DataFrame):
                    dml = kwargs["dml"]
                else:
                    dml = load_dml(kwargs["dml"], faidx=None)
                # Check that the file is not empty
                if dml.empty:
                    raise pd.errors.EmptyDataError('DML is empty')
                # the following assumes that `fastcat` / `bamstats` has been run
                # with `-s` which is not necessarily the case (if there was only
                # one sample) --> create a dummy 'sample_name' column if missing
                if 'sample_name' not in dml.columns:
                    dml['sample_name'] = 'sample'
                # If one sample, save one plot
                if len(dml['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    EZChart(karyomap(
                        dml, 'chrom', 'pos', 'fdr', ref_lengths=faidx), 'epi2melabs')
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in dml.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                EZChart(karyomap(
                                    df_sample, 'chrom', 'pos',
                                    'fdr', ref_lengths=faidx), 'epi2melabs')
            if "dmr" in kwargs:
                if isinstance(kwargs["dmr"], pd.DataFrame):
                    dmr = kwargs["dmr"]
                else:
                    dmr = load_dmr(kwargs["dmr"], faidx=faidx)
                # Check that the file is not empty
                if dmr.empty:
                    raise pd.errors.EmptyDataError('DMR is empty')
                # the following assumes that `fastcat` / `bamstats` has been run
                # with `-s` which is not necessarily the case (if there was only
                # one sample) --> create a dummy 'sample_name' column if missing
                if 'sample_name' not in dmr.columns:
                    dmr['sample_name'] = 'sample'
                # If one sample, save one plot
                if len(dmr['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    EZChart(karyomap(
                        dmr, 'chrom', 'start', 'areaStat',
                        ref_lengths=faidx, stats='median'),
                        'epi2melabs')
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in dmr.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                EZChart(karyomap(
                                    df_sample, 'chrom',
                                    'start', 'areaStats',
                                    ref_lengths=faidx, stats='median'), 'epi2melabs')


# Load diff. modified sites
def load_dml(dml, faidx=None, rename=None, order=None):
    """Load dml file.

    Input is either a single directory with all the DSS DML outputs or
    a single DSS DML file.

    Optional inputs can be:
    - faidx: A faidx dataframe with 'chrom' 'length' cols (add missing intervals)
    - rename: a dictionary used to rename the sequence IDs
    - order: a ordered karyotype (dictionary of "chrom" : int(position), e.g.
    {'chr1': 1, ..., 'chrY': 24})
    """
    relevant_stats_cols_dtypes = {
        "chr": CATEGORICAL,
        "pos": int,
        "mu1": float,
        "mu2": float,
        "diff": float,
        "diff.se": float,
        "stat": float,
        "phi1": float,
        "phi2": float,
        "pval": float,
        "fdr": float,
        "postprob.overThreshold": float,
    }
    # Check inputs
    dfs = []
    if os.path.isdir(dml):
        input_files = [(dml, i) for i in os.listdir(dml)]
    elif os.path.isfile(dml):
        input_files = [(None, dml)]
    else:
        raise Exception(f'No valid input: {dml}')
    # If no files, raise error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {dml}')
    # Process each file
    for (inpath, fname) in input_files:
        try:
            # Load the data
            dml_file = fname if not inpath else f'{inpath}/{fname}'
            tdf = pd.read_csv(dml_file, sep="\t", dtype=relevant_stats_cols_dtypes) \
                .rename(columns={'chr': 'chrom'}) \
                .eval("neg_log10_p = abs(log10(fdr))")
            if tdf.empty:
                cols = relevant_stats_cols_dtypes.update(
                    {'cum_pos': str, 'filename': int})
                dfs.append(pd.DataFrame(columns=cols))
                continue
            # Fix category names to use chrN format
            if rename:
                tdf['chrom'] = tdf['chrom'].cat.rename_categories(rename)
            if order:
                tdf = tdf \
                    .eval("chr_id = chrom.map(@order)") \
                    .sort_values(["chr_id", "pos"]) \
                    .drop(columns="chr_id")
            # Drop unused categories and reorder the remaining
            tdf['chrom'] = \
                tdf.chrom.cat.remove_unused_categories()
            tdf['chrom'] = \
                tdf.chrom.cat.reorder_categories(
                [i for i in tdf.chrom.unique()])
            # If the dataframe is empty, append it directly.
            if isinstance(faidx, pd.DataFrame):
                if 'length' not in faidx.columns:
                    raise ValueError(
                        'No "length" column found.',
                        'Import the fai with fasta_idx() and try again.')
                if 'chrom' not in faidx.columns:
                    raise ValueError(
                        'No "chrom" column found.',
                        'Import the fai with fasta_idx() and try again.')
                ref_lengths = faidx.groupby(
                    "chrom", observed=True, sort=False)["length"].last()
                total_ref_starts = ref_lengths.cumsum().shift(1, fill_value=0)
            else:
                # Compute reference lenghts from the input file
                ref_lengths = tdf.groupby(
                    "chrom", observed=True, sort=False)["pos"].last()
                # Compute cumulative position
                total_ref_starts = ref_lengths \
                    .cumsum() \
                    .shift(1, fill_value=0)
            # Compute the cumulative position.
            tdf["cum_pos"] = tdf.apply(
                lambda x: x.pos + total_ref_starts[x.chrom], axis=1)
            # Add file name
            tdf['filename'] = fname.split('/')[-1]
            # Add to output list
            dfs += [tdf
                    .reset_index(drop=True)]
        except pd.errors.EmptyDataError:
            cols = relevant_stats_cols_dtypes.update({'filename': str})
            dfs.append(pd.DataFrame(columns=cols))
    return pd.concat(dfs).reset_index(drop=True)


# Load diff. modified regions
def load_dmr(dmr, faidx=None, rename=None, order=None):
    """Load dmr file.

    Input is either a single directory with all the DSS DMR outputs or
    a single DSS DMR file.

    Optional inputs can be:
    - faidx: A faidx dataframe with 'chrom' 'length' cols (add missing intervals)
    - rename: a dictionary used to rename the sequence IDs
    - order: a ordered karyotype (dictionary of "chrom" : int(position), e.g.
    {'chr1': 1, ..., 'chrY': 24})
    """
    relevant_stats_cols_dtypes = {
        "chr": CATEGORICAL,
        "start": int,
        "end": int,
        "length": int,
        "nCG": int,
        "meanMethy1": float,
        "meanMethy2": float,
        "diff.Methy": float,
        "areaStat": float,
        }
    # Check inputs
    dfs = []
    if os.path.isdir(dmr):
        input_files = [(dmr, i) for i in os.listdir(dmr)]
    elif os.path.isfile(dmr):
        input_files = [(None, dmr)]
    else:
        raise Exception(f'No valid input: {dmr}')
    # If no files, raise error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {dmr}')
    # Process each file
    for (inpath, fname) in input_files:
        try:
            dmr_file = fname if not inpath else f'{inpath}/{fname}'
            tdf = pd.read_csv(
                    dmr_file,
                    sep="\t",
                    dtype=relevant_stats_cols_dtypes
                    ) \
                .rename(columns={'chr': 'chrom'}) \
                .eval('abs_diff = abs(`diff.Methy`)')\
                .drop(columns=['abs_diff']) \
                .eval("mean_pos=start+(length/2)") \
                .astype({'chrom': CATEGORICAL, 'mean_pos': int})
            # If it's empty, add an empty DF
            if tdf.empty:
                cols = relevant_stats_cols_dtypes.update(
                    {'cum_pos': str, 'filename': int})
                dfs.append(pd.DataFrame(columns=cols))
                continue
            # Rename categories if required
            if rename:
                tdf['chrom'] = tdf['chrom'].cat.rename_categories(rename)
            # Order the categories
            if order:
                tdf = tdf\
                    .eval("chr_id = chrom.map(@order)") \
                    .sort_values(["chr_id", "mean_pos"]) \
                    .drop(columns="chr_id")
            # If the dataframe is empty, append it directly.
            if tdf.empty:
                dfs.append(tdf.round(4))
                continue
            # If the dataframe is empty, append it directly.
            if isinstance(faidx, pd.DataFrame):
                if 'length' not in faidx.columns:
                    raise ValueError(
                        'No "length" column found.',
                        'Import the fai with fasta_idx() and try again.')
                if 'chrom' not in faidx.columns:
                    raise ValueError(
                        'No "chrom" column found.',
                        'Import the fai with fasta_idx() and try again.')
                ref_lengths = faidx.groupby(
                    "chrom", observed=True, sort=False)["length"].last()
                total_ref_starts = ref_lengths.cumsum().shift(1, fill_value=0)
            else:
                # Compute reference lenghts from the input file
                ref_lengths = tdf.groupby(
                    "chrom", observed=True, sort=False)["end"].last()
                # Compute cumulative position
                total_ref_starts = ref_lengths \
                    .cumsum() \
                    .shift(1, fill_value=0)
            # Compute the cumulative position.
            tdf["cum_pos"] = tdf.apply(
                lambda x: x.mean_pos + total_ref_starts[x.chrom], axis=1)
            # Add file name
            tdf['filename'] = fname.split('/')[-1]
            dfs.append(tdf.round(4))
        except pd.errors.EmptyDataError:
            cols = relevant_stats_cols_dtypes.update({'filename': str})
            dfs.append(pd.DataFrame(columns=cols))
    return pd.concat(dfs).reset_index(drop=True)


def main(args):
    """Entry point to demonstrate a differentially modified component."""
    comp_title = 'DML/DMR results'
    seq_sum = DMSummary(
        dml=args.dml,
        dmr=args.dmr,
        faidx=args.faidx
        )
    report = ComponentReport(comp_title, seq_sum)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'DSS summary',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--dml",
        default=resource_filename('ezcharts', "data/test/test_dml.tsv.gz"),
        help="Resulting differentially modified loci from DSS.")
    parser.add_argument(
        "--dmr",
        default=resource_filename('ezcharts', "data/test/test_dmr.tsv.gz"),
        help="Resulting differentially modified regions from DSS.")
    parser.add_argument(
        "--faidx", required=False,
        default=resource_filename('ezcharts', "data/test/ref.fa.fai"),
        help="Reference fasta fai index.")
    parser.add_argument(
        "--output",
        default="dss_report.html",
        help="Output HTML file.")
    return parser
