"""Parse single and multiple outputs from bcftools stats into dataframes."""

import argparse
from collections import defaultdict
import os
import re

import pandas as pd
from pandas.api import types as pd_types

from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import DataTable, Tabs
from ezcharts.plots.categorical import barplot


# Categorical types
CATEGORICAL = pd_types.CategoricalDtype(ordered=True)

# Multiple types structure for the different dataframes
coltypes = {
    'SN': {
        'filename': CATEGORICAL,
        'id': CATEGORICAL,
        'MNPs': int,
        'SNPs': int,
        'indels': int,
        'multiallelic SNP sites': int,
        'multiallelic sites': int,
        'no-ALTs': int,
        'others': int,
        'records': int,
        'samples': int,
    },
    'TSTV': {
        'filename': CATEGORICAL,
        'id': CATEGORICAL,
        'ts': int,
        'tv': int,
        'ts/tv': float,
        'ts (1st ALT)': int,
        'tv (1st ALT)': int,
        'ts/tv (1st ALT)': float
    },
    'SiS': {
        'filename': CATEGORICAL,
        'id': CATEGORICAL,
        'allele count': int,
        'number of SNPs': int,
        'number of transitions': int,
        'number of transversions': int,
        'number of indels': int,
        'repeat-consistent': int,
        'repeat-inconsistent': int,
        'not applicable': int
    },
    'AF': {
        'filename': CATEGORICAL,
        'id': CATEGORICAL,
        'allele frequency': float,
        'number of SNPs': int,
        'number of transitions': int,
        'number of transversions': int,
        'number of indels': int,
        'repeat-consistent': int,
        'repeat-inconsistent': int,
        'not applicable': int
    },
    'QUAL': {
        'filename': CATEGORICAL,
        'id': CATEGORICAL,
        'Quality': float,
        'number of SNPs': int,
        'number of transitions (1st ALT)': int,
        'number of transversions (1st ALT)': int,
        'number of indels': int
    },
    'IDD': {
        'filename': CATEGORICAL,
        'id': CATEGORICAL,
        'length (deletions negative)': int,
        'number of sites': int,
        'number of genotypes': int,
        'mean VAF': str   # mean VAF can be a '.' for single-sample VCFs, hence string
    }
}


class BcftoolsStats(Snippet):
    """Generate modified bases summary plots."""

    def __init__(self, theme='epi2melabs', **kwargs):
        """Create bcfstats summary report.

        If multiple single-sample stats are provided, each will be
        displayed in a distinct tab, with the exception of the summary table.

        :param stats: A path to a single-sample bcftools stats file or a pandas
            DataFrame from load_bcfstats
        :param sample_name: A string or list of strings specifying the sample names;
            it has to be of the same length as the input stats files
        """
        super().__init__(styles=None, classes=None)

        with self:
            # Make table of bcftools stats
            if "stats" in kwargs:
                if isinstance(kwargs["stats"], pd.DataFrame):
                    all_bcfstats = kwargs["stats"]
                else:
                    all_bcfstats = load_bcfstats(
                        kwargs["stats"], sample_names=kwargs["sample_names"])
                # Check that the file is not empty
                if len(all_bcfstats) == 0:
                    raise pd.errors.EmptyDataError('Input stats file is empty')
                # If one sample, save one plot
                for stat, table in all_bcfstats.items():
                    # Add base stats table
                    if stat == 'SN':
                        # we only got a single sample --> no dropdown
                        DataTable.from_pandas(
                            table, export=True, use_index=False)

                    # Showcase indel length
                    if stat == 'IDD':
                        if len(table['id'].unique()) == 1:
                            # we only got a single sample --> no dropdown
                            plt = barplot(
                                data=table,
                                x="length (deletions negative)",
                                y="number of sites")
                            plt.xAxis.axisLabel.rotate = 90
                            plt.xAxis.axisLabel.fontSize = 10
                            EZChart(plt, 'epi2melabs')
                        else:
                            # several samples --> use a dropdown menu
                            tabs = Tabs()
                            with tabs.add_dropdown_menu():
                                for fname, df_sample in table.groupby('id'):
                                    with tabs.add_dropdown_tab(fname):
                                        plt = barplot(
                                            data=table,
                                            x="length (deletions negative)",
                                            y="number of sites")
                                        plt.xAxis.axisLabel.rotate = 90
                                        plt.xAxis.axisLabel.fontSize = 10
                                        EZChart(plt, 'epi2melabs')


def split_blocks(fname):
    """Split lines of a file into blocks based on comment lines."""
    comment = list()
    data = list()
    state = None
    with open(fname, 'r') as fh:
        # TODO: handle empty tables
        for line in fh.readlines():
            if line.startswith('#'):
                if state != 'comment' and state is not None:
                    yield comment, data
                    comment, data = list(), list()
                state = 'comment'
                comment.append(line.strip('# ').rstrip())
            else:
                state = 'data'
                data.append(line.rstrip())
        yield comment, data


def parse_bcftools_stats(fname, sample_name=None):
    """Parse `bcftools stats` output.

    :param fname: file to parse.
    :param sample_name: name of the sample.
    """
    tables = dict()
    filename = fname.split('/')[-1]
    for comment, data in split_blocks(fname):
        fields = [x.rstrip() for x in re.split(r'\[\d+\]', comment[-1])]
        section, fields = fields[0], fields[1:]
        rows = list()
        for d in data:
            items = d.split('\t')
            if items[0] != section:
                raise ValueError("first data field not equal to section key")
            rows.append(items[1:])
        tables[section] = pd.DataFrame(rows, columns=fields)
        # Add file name as initial column in each of them
        tables[section].insert(0, 'filename', filename)
        # Add sample name if provided
        if sample_name:
            tables[section]['id'] = sample_name
        else:
            tables[section]['id'] = filename
    # now some special handling
    SN = tables['SN']
    SN['key'] = SN['key'].apply(
        lambda x: x.replace('number of ', '').rstrip(':'))
    tables['SN'] = pd.DataFrame(
        SN.pivot(index='id', columns='key', values='value').to_records())
    # Add file name as initial column in each of them
    tables['SN'].insert(0, 'filename', filename)
    # Add sample name if provided
    if sample_name:
        tables['SN']['id'] = sample_name
    else:
        tables['SN']['id'] = filename
    # Return tables
    return tables


def load_bcfstats(stats, sample_names=None):
    """Parse multiple bcf stats outputs and combine.

    :param fnames: list of filenames output by `bcftools stats.`
    :param samples_names: list of names of each sample to add to the
        dataframes.
    """
    # Check if it is one or more inputs
    if os.path.isdir(stats):
        filenames = [f"{stats}/{i}" for i in os.listdir(stats)]
    elif os.path.isfile(stats):
        filenames = [stats]
    else:
        raise Exception(f'No valid input: {stats}')

    # Check sample names
    if sample_names is not None:
        if len(sample_names) != len(filenames):
            raise TypeError(
                "`filenames` and `sample_names` should be of equal length.")
        zipped = zip(filenames, sample_names)
        dfs = [
            parse_bcftools_stats(filename, sample_name=sname)
            for (filename, sname) in zipped]
    else:
        dfs = [parse_bcftools_stats(filename) for filename in filenames]

    # Collect every table in one
    all_tables = defaultdict(list)
    for s_tables in dfs:
        # we don't use the 'id' field - its for intersections
        # and unions of two VCFs given to bcftools stats
        for stat, table in s_tables.items():
            all_tables[stat].append(table)
    for stat, tables in all_tables.items():
        if stat in coltypes:
            all_tables[stat] = pd.concat(tables).astype(coltypes[stat])
        else:
            all_tables[stat] = pd.concat(tables).infer_objects()
    return all_tables


def main(args):
    """Entry point to demonstrate the bcftools stats."""
    comp_title = 'BCFtools stats'
    sample_names = args.sample_name if args.sample_name else None
    stats = BcftoolsStats(stats=args.stats, sample_names=sample_names)
    report = ComponentReport(comp_title, stats)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'BCFtools stats',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--stats",
        required=True,
        help="Input bcftools stats file.")
    parser.add_argument(
        "--sample_name",
        help="Name of the sample; valid for a single sample.")
    parser.add_argument(
        "--output",
        default="bcfstats_report.html",
        help="Output HTML file.")
    return parser
