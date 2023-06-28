"""Visualizing matrices of data."""
import numpy as np
import pandas as pd
import seaborn as sns

import ezcharts as ezc
from ezcharts.components.common import make_breaks


__all__ = ["karyomap"]


def karyomap(
        df, chrom, pos, value, stats='count',
        order=None, palette="crest", window_size=1000000,
        ref_lengths=None, borders=True, labels=True,
        min_sequence_size=None, include_small_ctgs=False):
    """
    Plot chromosomal heatmap in windows of a given size.

    Accepts a dataset with at least three columns:
    - chromosome (y axis)
    - positions (x axis)
    - values (colour intensity)

    The dataset is collected in bins of given size, with the following stats
    availabe:
    - count
    - mean
    - median

    A custom ordering can be specified, but if not it will sort by sequence size.

    By default, the plot will represent only sequences longer than the window size
    (i.e. if window_size=1Mb, then sequences of 999,999bp and smaller won't be shown).

    The default palette uses dark-to-light colours for lower-to-higher values.

    If ref_lengths is not provided, the script will use the highest position in the
    dataset.
    """
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)

    def build_intervals(ctgid, start, end, size):
        """Build a dataframe of intervals."""
        breaks = make_breaks(start, end, size)
        return pd.DataFrame(
            data={
                'chr': ctgid,
                'start': breaks[0:-1],
                'end': breaks[1:]})

    # Compute central value.
    def compute_value(data, x, col='values', stats=stats):
        """Return the average of a given column in a region."""
        data_ = data[(data[chrom] == x.chr) &
                     (data[pos] >= x.start) &
                     (data[pos] < x.end)]
        if stats == 'count':
            return data_.shape[0]
        if stats == 'median':
            return data_[col].median()
        elif stats == 'mean':
            return data_[col].mean()
        else:
            raise ValueError("stats must be one of 'count', 'mean', or 'median'")

    # If no ref_length, define it from the positions
    if ref_lengths is None:
        ref_lengths = df.groupby(chrom).max()[pos].reset_index()
        ref_lengths.columns = ['chrom', 'length']

    # Check that ref_length contains the right columns.
    if 'length' not in ref_lengths.columns:
        raise ValueError(
            'No "length" column found.',
            'Import the fai with fasta_idx() and try again.')
    if 'chrom' not in ref_lengths.columns:
        raise ValueError(
            'No "chrom" column found.',
            'Import the fai with fasta_idx() and try again.')

    # Drop all sequences that are smaller than the window size.
    # This prevents having N rows in the heatmap, where N is >2000 for hg38
    # The default behaviour is to keep sequences larger than the window size,
    # but alternatively a specific size can be enforced with min_sequence_size.
    # Finally, users can use all contigs regardless with include_small_ctgs
    if include_small_ctgs is False:
        if isinstance(min_sequence_size, int):
            ref_lengths = ref_lengths.loc[ref_lengths.length > min_sequence_size]
        else:
            ref_lengths = ref_lengths.loc[ref_lengths.length > window_size]

    # Build intervals to visualize
    intervals = pd.concat([
        build_intervals(r.chrom, 0, r.length, window_size)
        for idx, r in ref_lengths.iterrows()])

    # Compute median -log10(P-value) for each interval
    intervals['value'] = intervals.apply(
        lambda x: compute_value(df, x, col=value, stats=stats), axis=1)
    intervals = intervals.fillna(0).replace([np.inf, -np.inf], 0)

    # Transpose the matrix
    mat = intervals.pivot(index='start', columns='chr', values='value')

    # Define new index as window intervals with format start_pos-end_pos
    new_idx = pd.Series(
        [f'{c}-{c + window_size}'
            for c in mat.index.astype('int')])
    mat = mat.set_index(new_idx)

    # Keep chromosomes only and reorder them.
    # Reverse ordering needed to have the first on top.
    if order:
        cols = [
            col for col in order if col in mat.columns][::-1]
    else:
        cols = ref_lengths.sort_values('length', ascending=True).chrom.values
    mat = mat[cols]

    # Define color map
    colmap = sns.color_palette(palette, n_colors=1000, as_cmap=False).as_hex()

    # Create the heatmap
    plt = ezc.heatmap(mat, annot=False, cmap=colmap)
    # Make Y-axis labels smaller and show all of them
    plt.yAxis.axisLabel = dict(fontSize=10, interval=0)
    # Remove unnecessary X labels since too many
    plt.xAxis.axisLabel = dict(show=False)
    # Add borders to the heatmap cells
    if borders:
        for s in plt.series:
            s.itemStyle = dict(
                borderColor='white',
                borderWidth=1
            )
    # Add tooltips
    if labels:
        plt.tooltip = dict(show=True)
    return plt
