"""An ezcharts component for loading modkit data."""
import argparse
import os

import pandas as pd
from pandas.api import types as pd_types
from pkg_resources import resource_filename

from ezcharts.components.common import fasta_idx, MOD_CONVERT
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import DataTable, Tabs
from ezcharts.plots.karyomap import karyomap

# Categorical types
CATEGORICAL = pd_types.CategoricalDtype(ordered=True)


class MKSummary(Snippet):
    """Generate modified bases summary plots."""

    def __init__(self, theme='epi2melabs', **kwargs):
        """Create depth summary componet.

        If dml/dmr contains results from multiple samples, each will be
        plotted in its own tab.

        :param modkit_summary: A path to a modkit summary output file or
            DataFrame
        :param bedmethyl: A path to a modkit bedmethyl output file or
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
            if "modkit_summary" in kwargs:
                if isinstance(kwargs["modkit_summary"], pd.DataFrame):
                    summary = kwargs["modkit_summary"]
                else:
                    summary = load_modkit_summary(kwargs["modkit_summary"])
                # Check that the file is not empty
                if summary.empty:
                    raise pd.errors.EmptyDataError('Summary is empty')
                # the following assumes that `fastcat` / `bamstats` has been run
                # with `-s` which is not necessarily the case (if there was only
                # one sample) --> create a dummy 'sample_name' column if missing
                if 'sample_name' not in summary.columns:
                    summary['sample_name'] = 'sample'
                # If one sample, save one plot
                if len(summary['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    DataTable.from_pandas(summary, use_index=False)
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in summary.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                DataTable.from_pandas(df_sample, use_index=False)
            # Make modkit bedmethyl karyomap
            if "bedmethyl" in kwargs:
                if isinstance(kwargs["bedmethyl"], pd.DataFrame):
                    bedmethyl = kwargs["bedmethyl"]
                else:
                    bedmethyl = load_bedmethyl(
                        kwargs["bedmethyl"], faidx=faidx, split_all=True)
                # Check that the file is not empty
                if bedmethyl.empty:
                    raise pd.errors.EmptyDataError('Bedmethyl is empty')
                # the following assumes that `fastcat` / `bamstats` has been run
                # with `-s` which is not necessarily the case (if there was only
                # one sample) --> create a dummy 'sample_name' column if missing
                if 'sample_name' not in bedmethyl.columns:
                    bedmethyl['sample_name'] = 'sample'
                # If one sample, save one plot
                if len(bedmethyl['sample_name'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    EZChart(karyomap(
                        bedmethyl, 'chrom', 'start',
                        'score', ref_lengths=faidx), 'epi2melabs')
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in bedmethyl.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                EZChart(karyomap(
                                    df_sample, 'chrom',
                                    'pos', 'fdr', ref_lengths=faidx), 'epi2melabs')


# Load mod bedMethyl file
def load_modkit_summary(summary_dir):
    """Load bedmethyl file.

    Input is either a single directory with all the modkit summaries or
    a single modkit summary file.
    """
    # Col names
    relevant_stats_cols_dtypes = {
        "sample": CATEGORICAL,
        "type": CATEGORICAL,
        "base": CATEGORICAL,
        "code": CATEGORICAL,
        "pass_count": int,
        "pass_frac": float,
        "all_counts": int,
        "all_frac": float,
    }
    # Prepare input files
    dfs = []
    if os.path.isdir(summary_dir):
        input_files = [(summary_dir, i) for i in os.listdir(summary_dir)]
    elif os.path.isfile(summary_dir):
        input_files = [(None, summary_dir)]
    else:
        raise Exception(f'No valid input: {summary_dir}')
    # If no files, raise error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {summary_dir}')
    # Process each file
    for (inpath, fname) in input_files:
        try:
            f_path = fname if not inpath else f'{inpath}/{fname}'
            try:
                df = pd.read_csv(
                    f_path,
                    dtype=relevant_stats_cols_dtypes,
                    sep='\t',
                    comment='#')
            except TypeError:
                df = pd.read_csv(
                    f_path,
                    names=relevant_stats_cols_dtypes,
                    dtype=relevant_stats_cols_dtypes,
                    sep='\t',
                    comment='#')
            # If it's empty, add an empty DF
            if df.empty:
                cols = relevant_stats_cols_dtypes.update(
                    {'mod': str, 'threshold': str, 'filename': int})
                dfs.append(pd.DataFrame(columns=cols))
                continue
            # Convert modification to the appropriate code
            df['mod'] = df.apply(
                lambda x: MOD_CONVERT.get(x.code, x.base), axis=1)
            df.astype({'mod': CATEGORICAL})
            # Read and add the thresholds value
            for line in open(f_path):
                line = line.strip().split()
                if line[1] == 'pass_threshold_C':
                    threshold = float(line[2])
                    break
            df['threshold'] = threshold
            # Add file name
            df['filename'] = fname.split('/')[-1]
            # Ensure that the mod-base code is consistent
            dfs.append(df)
        except pd.errors.EmptyDataError:
            cols = relevant_stats_cols_dtypes.update({'filename': str})
            dfs.append(pd.DataFrame(columns=cols))
    return pd.concat(dfs).reset_index(drop=True)


def load_bedmethyl(bedmethyl_input, faidx=None, split_all=False):
    """Load modkit bedmethyl file.

    Input is either a single directory with all the modkit bedmethyls or
    a single modkit bedmethyl file.

    Optional inputs can be:
    - faidx: A faidx dataframe with 'chrom' 'length' cols (add missing intervals)
    """
    # Col names
    long_cols_dtypes = {
        "chrom": CATEGORICAL,
        "start": int,
        "end": int,
        "mod": CATEGORICAL,
        "score": int,
        "strand": CATEGORICAL,
        "startp": int,
        "endp": int,
        "colour": CATEGORICAL,
        "Nvalid": int,
        "fraction": float,
        "Nmod": int,
        "Ncanonical": int,
        "Nother_mod": int,
        "Ndelete": int,
        "Nfail": int,
        "Ndiff": int,
        "Nnocall": int,
    }
    short_cols_dtypes = {
        'chrom': CATEGORICAL,
        'start': int,
        'end': int,
        'mod': str,
        'score': int,
        'strand': str,
        'start_p': int,
        'end_p': int,
        "colour": CATEGORICAL,
        'vals': str,
    }
    # Check inputs
    dfs = []
    if os.path.isdir(bedmethyl_input):
        input_files = [(bedmethyl_input, i) for i in os.listdir(bedmethyl_input)]
    elif os.path.isfile(bedmethyl_input):
        input_files = [(None, bedmethyl_input)]
    else:
        raise Exception(f'No valid input: {bedmethyl_input}')
    # If no input files are found, raise error
    if len(input_files) == 0:
        raise FileNotFoundError(f'No valid input found in {bedmethyl_input}')
    # Process each file
    for (inpath, fname) in input_files:
        try:
            bedmethyl = fname if not inpath else f'{inpath}/{fname}'
            # Load input bedmethyl
            if split_all is True:
                cols = long_cols_dtypes
                df = pd.read_csv(
                    bedmethyl,
                    sep="\t| ",
                    engine='python',
                    names=cols.keys(),
                    dtype=cols)
            else:
                cols = short_cols_dtypes
                df = pd.read_csv(
                    bedmethyl,
                    sep="\t",
                    engine='python',
                    names=short_cols_dtypes.keys(),
                    dtype=short_cols_dtypes)
            # If it's empty, add an empty DF
            if df.empty:
                cols = cols.update(
                    {'total_mean_pos': str, 'filename': int})
                dfs.append(pd.DataFrame(columns=cols))
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
                ref_lengths = df.groupby(
                    "chrom", observed=True, sort=False)["end"].last()
                # Compute cumulative position
                total_ref_starts = ref_lengths \
                    .cumsum() \
                    .shift(1, fill_value=0)
            # Compute the cumulative position.
            df["total_mean_pos"] = df.apply(
                lambda x: x.start + total_ref_starts[x.chrom], axis=1)
            # Add file name
            df['filename'] = fname.split('/')[-1]
            # Add to output list
            dfs.append(df)
        except pd.errors.EmptyDataError:
            if split_all is True:
                cols = long_cols_dtypes.update({'filename': str})
            else:
                cols = short_cols_dtypes.update({'filename': str})
            dfs.append(pd.DataFrame(columns=cols))
    return pd.concat(dfs).reset_index(drop=True)


def main(args):
    """Entry point to demonstrate a modkit component."""
    comp_title = 'ModKit results'
    seq_sum = MKSummary(
        modkit_summary=args.modkit_summary,
        bedmethyl=args.bedmethyl,
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
        "--modkit_summary",
        default=resource_filename('ezcharts', "data/test/test_modkit_summary.tsv"),
        help="Resulting summary file from modkit summary.")
    parser.add_argument(
        "--bedmethyl",
        default=resource_filename('ezcharts', "data/test/test_modkit.bed.gz"),
        help="Resulting bedmethyl file from modkit pileup.")
    parser.add_argument(
        "--faidx", required=False,
        default=resource_filename('ezcharts', "data/test/ref.fa.fai"),
        help="Reference fasta fai index.")
    parser.add_argument(
        "--output",
        default="modkit_report.html",
        help="Output HTML file.")
    return parser
