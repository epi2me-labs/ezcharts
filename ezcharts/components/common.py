"""An ezcharts component for common parsers."""
import pandas as pd
from pandas.api import types as pd_types

# Categorical types
CATEGORICAL = pd_types.CategoricalDtype(ordered=True)

# Fix order of modified base type when displying to keep everything consistent
MOD_ORDER = [
    f'{mod}{strand}' for mod in
    ['5mC', '5hmC', '5fC', '5caC', 'modC', '5hmU',
     '5fU', '5caU', 'modT', '6mA', 'modA', '8oxoG',
     'modG', 'Xao', 'modN'] for strand in ['', '_+', '_-']]
# SAM modification codes to human-readable codes
MOD_CONVERT = {
    'm': '5mC',
    'h': '5hmC',
    'f': '5fC',
    'c': '5caC',
    'C': 'modC',
    'g': '5hmU',
    'e': '5fU',
    'b': '5caU',
    'T': 'modT',
    'a': '6mA',
    'A': 'modA',
    'o': '8oxoG',
    'G': 'modG',
    'n': 'Xao',
    'N': 'modN'
}

# Human chromosome order
HSA_CHROMOSOME_ORDER = [f'chr{i}' for i in range(1, 23)] + ['chrX', 'chrY']

# ClinVar/NCBI info
CLINVAR_BASE = "https://www.ncbi.nlm.nih.gov/clinvar/variation/"
NCBI_BASE = "https://www.ncbi.nlm.nih.gov/gene/"
CLINVAR_DOCS_URL = "https://www.ncbi.nlm.nih.gov/clinvar/docs/clinsig/"


# Load faidx
def fasta_idx(faidx, rename=None):
    """Read faidx for the reference fasta."""
    relevant_stats_cols_dtypes = {
        "chrom": CATEGORICAL,
        "length": int,
        "offset1": int,
        "offset2": int,
        "offset3": int,
    }
    try:
        df = pd.read_csv(
            faidx,
            sep="\t",
            names=relevant_stats_cols_dtypes.keys(),
            usecols=relevant_stats_cols_dtypes.keys(),
            dtype=relevant_stats_cols_dtypes,
        )
        if rename:
            df['chrom'] = df['chrom'].cat.rename_categories(rename)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=relevant_stats_cols_dtypes)
    return df


def make_breaks(minval, maxval, winsize):
    """Create intervals inclusive of last value.

    This takes a initial value, a final value and an interval size.
    It then create the interval using range, and checks if the last value
    matches maxval. If not, it adds it back.
    For example, "range(0, 10001, 1000)" would generate a set of breaks
    [0, 1000, 2000, ..., 10000]
    Leaving out 10001. The function then adds it back to the list.

    This is relevant when creating sliding windows of given size in a
    chromosome to avoid losing the telomeric ends of the genome.
    """
    # Create the intervals
    breaks = list(range(minval, maxval, winsize))
    # Check that the max value is the chr length
    if breaks[-1] < maxval:
        breaks += [maxval]
    return breaks


def add_missing_windows(intervals, faidx, value='value', winsize=25000):
    """Add missing windows to value dataframe.

    If the value refers to a narrow region of the chromosome, this will
    cause to generate a dataframe with either a single-entry, or only
    few entries. This causes the production of poor quality or impossible to
    understand plots.
    This function fixes this by adding the missing leading or trailing
    intervals, matching the full length of the chromosome. Moreover, it will
    check for the presence of gaps in the region, adding back the missing
    points. All added intervals are set to 0-coverage values.
    """
    # Instantiate column types
    relevant_stats_cols_dtypes = {
        "chrom": CATEGORICAL,
        "start": int,
        "end": int,
        value: float,
    }
    # Ensure it is sorted
    intervals = intervals.sort_values(['chrom', 'start'])
    # Get unique chromosomes
    chrs = faidx.query(f'length>={winsize}').chrom.unique().tolist()
    # New intervals
    final_intervals = []
    # Add missing windows for each chromosome
    for chr_id in chrs:
        # Get chromosome entries
        chr_entry = intervals.loc[intervals['chrom'] == chr_id].reset_index(drop=True)
        # First window start
        minval = chr_entry.start.min() if not chr_entry.empty \
            else faidx[faidx['chrom'] == chr_id].length.max()
        # Final window end
        maxval = faidx[faidx['chrom'] == chr_id].length.max()
        # Chromosome length
        chr_len = faidx[faidx['chrom'] == chr_id].length.max()
        # If the minimum value is != 0, add intermediate windows
        if minval != 0:
            # Create the breaks for the intervals
            breaks = make_breaks(0, minval, winsize)
            # Add leading intervals
            final_intervals.append(
                pd.DataFrame(data={
                    'chrom': chr_id,
                    'start': breaks[0:-1],
                    'end': breaks[1:],
                    value: 0}))
        # Append precomputed intervals, checking for breaks
        # in between regions.
        for idx, region in chr_entry.iterrows():
            # To DF
            region = region.to_frame().T
            # Add the first window as default
            if idx == 0:
                final_intervals.append(region)
                continue
            # If the new window start is not the end of the previous,
            # then create new regions
            if region.start.min() != final_intervals[-1].end.max():
                # Create intervals
                breaks = make_breaks(
                    final_intervals[-1].end.max(),
                    region.start.min(),
                    winsize)
                # Add heading    intervals
                final_intervals.append(
                    pd.DataFrame(data={
                        'chrom': chr_id,
                        'start': breaks[0:-1],
                        'end': breaks[1:],
                        value: 0}))
            final_intervals.append(region)
        # If the max value is less than the chromosome length, add these too
        if maxval < chr_len:
            # Create the breaks for the intervals
            breaks = make_breaks(maxval, chr_len, winsize)
            # Create vectors to populate the DF
            chr_vec = [chr_id] * (len(breaks) - 1)
            values = [0] * (len(breaks) - 1)
            # Add tailing intervals
            final_intervals.append(
                pd.DataFrame(data={
                    'chrom': chr_vec,
                    'start': breaks[0:-1],
                    'end': breaks[1:],
                    value: values}))
    return pd.concat(final_intervals).astype(
        relevant_stats_cols_dtypes).reset_index(drop=True)
