"""An ezcharts component to calculate poly(A) tail metrics."""
import re

from bokeh.models import Title
import numpy as np
import pandas as pd
import pysam
from scipy import stats

import ezcharts as ezc


def _get_percent(num, den):
    """Calculate percent."""
    return (num / den) * 100 if den != 0 else 0


def _generate_histogram_data(lengths, binwidth=1, min_val=0, max_val=0):
    """Generate histogram data."""
    if len(lengths) > 0:
        min_val = int(min(lengths))
        max_val = int(max(lengths))
    values, bins = np.histogram(
        lengths, bins=range(min_val, max_val + binwidth + 1, binwidth))
    return list(map(list, zip(bins, values)))


def _interpret_kurtosis_value(value):
    """Determine interpretation string for kurtosis result."""
    if value is None or np.isnan(value):
        return ""
    elif value > 0.5:
        return "(more outliers compared to normality)"
    elif value < -0.5:
        return "(fewer outliers compared to normality)"
    else:
        return "(close to normally distributed)"


def load_reads_from_bam(
        bam_file_path, include_secondary=False,
        include_supplementary=False, include_reverse=False,
        include_no_tail=False):
    """Load reads from BAM file into a DataFrame.

    :param bam_file_path: Path to BAM file with poly(A) tail information.
    :param include_secondary: Whether to include secondary alignments.
    :param include_supplementary: Whether to include supplementary alignments.
    :param include_reverse: Whether to include reverse strand reads.
    :param include_no_tail: Whether to include reads with no poly(A) tail.

    :returns: DataFrame containing per-read data.
    """
    if not isinstance(bam_file_path, str):
        raise ValueError("bam_file_path must be a path to a BAM file.")

    # Process BAM file
    samfile = pysam.AlignmentFile(bam_file_path, "rb")
    # Get reference length
    ref_lengths = dict(enumerate(samfile.lengths))

    reads = []
    for read in samfile.fetch():

        # Skip split reads (reads with 'pi' tag)
        if read.has_tag('pi'):
            continue

        # Skip secondary reads unless explicitly included
        if read.is_secondary and not include_secondary:
            continue

        # Skip supplementary reads unless explicitly included
        if read.is_supplementary and not include_supplementary:
            continue

        # Skip unmapped reads
        if not read.is_mapped:
            continue

        # Only process fwd reads for now (even if circular)
        if not read.is_forward and not include_reverse:
            continue

        # 0 and -1 are valid pt tags so we need to differentiate
        # between no tag and a tag with value 0
        # Many linearised rbk reads won't have a tail (dorado -1)
        if not read.has_tag("pt"):
            pt = -2
        else:
            pt = read.get_tag('pt')

        # Skip reads with negative pt tags unless explicitly included
        if pt < 0 and not include_no_tail:
            continue

        reads.append({
            'read_id': read.query_name,
            'flag': read.flag,
            'qscore': read.get_tag('qs') if read.has_tag('qs') else 0,
            'polya': pt,
            'direction': '+' if read.is_forward else '-',
            'read_length': read.query_length,
            'ref_length': ref_lengths[read.reference_id]
        })

    all_reads = pd.DataFrame(reads)
    return all_reads


def filter_polya_reads(
        all_reads, read_length_tolerance_percent=10,
        quality_threshold=10, read_flag=0,
        filter_primary=False, filter_high_qs=False, filter_forward=False,
        filter_has_tail=False, filter_len_range=False):
    """Filter reads DataFrame for poly(A) analysis.

    :param all_reads: DataFrame of reads from load_reads_from_bam().
    :param read_length_tolerance_percent: Percentage tolerance for read
        length filtering.
    :param quality_threshold: Minimum quality score threshold.
    :param read_flag: Read flag for filtering (default 0 for primary reads).
    :param filter_primary: Whether to filter for primary alignments.
    :param filter_high_qs: Whether to filter for high quality scores.
    :param filter_forward: Whether to filter for forward strand reads.
    :param filter_has_tail: Whether to filter for reads with poly(A) tail.
    :param filter_len_range: Whether to filter for reads within length range.

    :returns: Filtered DataFrame.
    """
    if all_reads.empty:
        return all_reads

    # Apply per-read length bounds based on ref_length
    all_reads["min_len"] = \
        all_reads["ref_length"] * (1 - read_length_tolerance_percent / 100)
    all_reads["max_len"] = \
        all_reads["ref_length"] * (1 + read_length_tolerance_percent / 100)

    # Individual masks
    is_primary_forward = all_reads["flag"] == read_flag
    is_high_qs = all_reads["qscore"] >= quality_threshold
    is_forward = all_reads["direction"] == '+'
    has_tail = all_reads["polya"] > 0
    in_len_range = ((all_reads["read_length"] >= all_reads["min_len"]) &
                    (all_reads["read_length"] <= all_reads["max_len"]))

    # Start with everything included
    mask = pd.Series(True, index=all_reads.index)

    # Apply filters conditionally
    if filter_primary:
        mask &= is_primary_forward
    if filter_high_qs:
        mask &= is_high_qs
    if filter_forward:
        mask &= is_forward
    if filter_has_tail:
        mask &= has_tail
    if filter_len_range:
        mask &= in_len_range

    return all_reads[mask]


def calculate_polya_metrics(
        all_reads, filtered_reads, lower_bound, upper_bound,
        polya_reference_length, tail_interruption=None,
        output_percent_no_tail=False):
    """Calculate poly(A) tail metrics from pre-loaded and filtered reads.

    :param all_reads: Unfiltered DataFrame from load_reads_from_bam().
    :param filtered_reads: Filtered DataFrame from filter_polya_reads().
    :param lower_bound: Lower bound for poly(A) length classification.
    :param upper_bound: Upper bound for poly(A) length classification.
    :param polya_reference_length: Poly(A) reference length for filtering.
    :param tail_interruption: Tail interruption sequence (e.g., "GCC").
    :param output_percent_no_tail: Whether to include percent of reads
        with no poly(A) tail.

    :returns: Dictionary containing poly(A) tail metrics.
    """
    # Input validation following fastcat.py patterns
    if lower_bound >= upper_bound:
        raise ValueError(
            f"Lower bound ({lower_bound}) must be less than "
            f"upper bound ({upper_bound})")

    if tail_interruption:
        if not isinstance(tail_interruption, str):
            raise ValueError(
                "tail_interruption should be a string, "
                f"got {type(tail_interruption).__name__}")
        else:
            if re.search(r'[^ATCG]', tail_interruption.upper()):
                raise ValueError(
                    f"Invalid tail_interruption: '{tail_interruption}'. "
                    "Only A, T, C, G characters are allowed.")

    if all_reads.empty:
        metrics = _empty_metrics_dict()
        if output_percent_no_tail:
            metrics['percent_no_tail'] = 0
    else:
        # Calculate metrics
        metrics = _calculate_polya_statistics(
            filtered_reads['polya']
            if not filtered_reads.empty
            else pd.Series(dtype=float),
            lower_bound, upper_bound)

        if output_percent_no_tail:
            metrics['percent_no_tail'] = _get_percent(
                len(all_reads[all_reads["polya"] <= 0]),
                len(all_reads))

    # Add configuration info for reporting
    metrics.update({
        'reference_length': polya_reference_length,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound
    })
    if tail_interruption:
        metrics['tail_interruption'] = tail_interruption

    return metrics


def load_polya_metrics(
        bam_file_path, lower_bound, upper_bound,
        polya_reference_length, read_length_tolerance_percent=10,
        quality_threshold=10, read_flag=0, tail_interruption=None,
        include_secondary=False, include_supplementary=False,
        include_reverse=False, include_no_tail=False,
        output_percent_no_tail=False, filter_primary=False,
        filter_high_qs=False, filter_forward=False,
        filter_has_tail=False, filter_len_range=False,
        return_dataframe=False):
    """Load and calculate poly(A) tail metrics from BAM file.

    Convenience wrapper around load_reads_from_bam, filter_polya_reads
    and calculate_polya_metrics for cases where access to the intermediate
    DataFrames is not required.

    :param bam_file_path: Path to BAM file with poly(A) tail information.
    :param lower_bound: Lower bound for poly(A) length classification.
    :param upper_bound: Upper bound for poly(A) length classification.
    :param polya_reference_length: Poly(A) reference length for filtering.
    :param read_length_tolerance_percent: Percentage tolerance for read
        length filtering.
    :param quality_threshold: Minimum quality score threshold.
    :param read_flag: Read flag for filtering (default 0 for primary reads).
    :param tail_interruption: Tail interruption sequence (e.g., "GCC").
    :param include_secondary: Whether to include secondary alignments
        (default False).
    :param include_supplementary: Whether to include supplementary alignments
        (default False).
    :param include_reverse: Whether to include reverse strand reads.
    :param include_no_tail: Whether to include reads with no poly(A) tail.
    :param output_percent_no_tail: Whether to include percent of reads
        with no poly(A) tail.
    :param filter_primary: Whether to filter for primary alignments.
    :param filter_high_qs: Whether to filter for high quality scores.
    :param filter_forward: Whether to filter for forward strand reads.
    :param filter_has_tail: Whether to filter for reads with poly(A) tail.
    :param filter_len_range: Whether to filter for reads within length range.

    :returns: Dictionary containing poly(A) tail metrics, or tuple of
        (metrics dict, all_reads DataFrame, filtered_reads DataFrame)
        if return_dataframe is True
    """
    all_reads = load_reads_from_bam(
        bam_file_path,
        include_secondary=include_secondary,
        include_supplementary=include_supplementary,
        include_reverse=include_reverse,
        include_no_tail=include_no_tail)

    filtered_reads = filter_polya_reads(
        all_reads,
        read_length_tolerance_percent=read_length_tolerance_percent,
        quality_threshold=quality_threshold,
        read_flag=read_flag,
        filter_primary=filter_primary,
        filter_high_qs=filter_high_qs,
        filter_forward=filter_forward,
        filter_has_tail=filter_has_tail,
        filter_len_range=filter_len_range)

    metrics = calculate_polya_metrics(
        all_reads, filtered_reads,
        lower_bound, upper_bound,
        polya_reference_length,
        tail_interruption=tail_interruption,
        output_percent_no_tail=output_percent_no_tail)

    if return_dataframe:
        return metrics, all_reads, filtered_reads
    return metrics


def _empty_metrics_dict():
    """Return empty metrics dictionary for edge cases."""
    return {
        'histogram': [[0, 0]],
        'percent_in_bounds': 0.0,
        'total_area': 0.0,
        'area_with': 0.0,
        'percent_polya_area': 0.0,
        'percent_present': 0.0,
        'mean_length': 0.0,
        'median_length': 0.0,
        'std_dev_length': 0.0,
        'kurtosis_length': None,
        'mode_length': 0.0,
        'confidence_interval_length': (0.0, 0.0)
    }


def _calculate_polya_statistics(lengths, lower_bound, upper_bound):
    """Calculate poly(A) tail statistics from length data."""
    if lengths.empty:
        return _empty_metrics_dict()
    in_bounds = lengths[(lengths >= lower_bound) & (lengths <= upper_bound)]
    with_polya = lengths[lengths >= lower_bound]
    mean = lengths.mean()
    median = np.median(lengths)
    mode = float(lengths.mode().iloc[0]) if not lengths.mode().empty else 0

    # Only calculate CI, std and kurtosis when we have more than one read
    # and not all values are zero
    std = 0.0
    ci = (0.0, 0.0)
    kurtosis = None
    if lengths.size > 1 and not np.all(lengths == 0):
        std = lengths.std(ddof=1)
        ci = stats.t.interval(
            0.95, len(lengths)-1, loc=mean, scale=std/np.sqrt(len(lengths)))
        kurtosis = stats.kurtosis(lengths, fisher=True)
        # Convert NaN kurtosis to None
        if np.isnan(kurtosis):
            kurtosis = None

    return {
        'histogram': _generate_histogram_data(lengths),
        'percent_in_bounds': _get_percent(len(in_bounds), len(lengths)),
        'total_area': lengths.sum(),
        'area_with': with_polya.sum(),
        'percent_polya_area': _get_percent(with_polya.sum(), lengths.sum()),
        'percent_present': _get_percent(len(with_polya), len(lengths)),
        'mean_length': mean,
        'median_length': median,
        'std_dev_length': std,
        'kurtosis_length': kurtosis,
        'mode_length': mode,
        'confidence_interval_length': ci,
    }


def format_polya_summary(metrics):
    """Format poly(A) metrics for display in reports."""
    kurtosis_interpretation = _interpret_kurtosis_value(
        metrics['kurtosis_length'])

    # Handle kurtosis display when None
    kurtosis_value = (
        "Not applicable" if metrics['kurtosis_length'] is None
        else round(metrics['kurtosis_length'], 2)
    )

    # Special case, if only 1 read present, don't show confidence interval
    polya_read_count = sum(int(count) for _, count in metrics['histogram'])
    if polya_read_count > 1:
        mean_key = "Mean (95% CI)"
        mean_display = (
            f"({round(metrics['confidence_interval_length'][0], 2)})"
            f" {round(metrics['mean_length'], 2)}"
            f" ({round(metrics['confidence_interval_length'][1], 2)})")
    else:
        mean_key = "Mean"
        mean_display = f"{round(metrics['mean_length'], 2)}"

    output = {
        "Reference length": f"{metrics['reference_length']}b",
        "Median length": metrics['median_length'],
        mean_key: mean_display,
        "Mode": metrics['mode_length'],
        "Percent Poly(A)": round(metrics['percent_present'], 2),
        "Percent in length bounds": (
            f"({round(metrics['lower_bound'], 2)})"
            f" {round(metrics['percent_in_bounds'], 2)}"
            f" ({round(metrics['upper_bound'], 2)})"),
    }

    if 'percent_no_tail' in metrics:
        output["Percent reads no Poly(A)"] = round(
            float(metrics['percent_no_tail']), 2)

    output["Kurtosis deviation from normality"] = (
        f"{kurtosis_value} {kurtosis_interpretation}")

    output["Tail interruption"] = (
        metrics['tail_interruption']
        if metrics.get('tail_interruption')
        else "No interruption specified"
    )

    return output


@ezc.plots.util.plot_wrapper
def polya_histogram_plot(metrics, color='#007FA9'):
    """Create histogram plot from poly(A) metrics.

    :param metrics: Dictionary containing poly(A) metrics with 'histogram' key.
    :param color: Color for the histogram bars.

    :returns: EZChart plot object.
    """
    histogram = metrics['histogram']
    if not histogram:
        return ezc.plots.util.empty_plot(
            text="Poly(A) tail length",
            subtext="No poly(A) tail data to plot.")

    poly_a_raw = []
    for bin_val, count in histogram:
        poly_a_raw.extend([int(bin_val)] * int(count))

    if not poly_a_raw:
        return ezc.plots.util.empty_plot(
            text="Poly(A) tail length",
            subtext="No Poly(A) tail data to plot.")

    polya_plot = ezc.histplot(
        poly_a_raw,
        binwidth=1,
        stat='count',
        color=color)

    polya_plot._fig.x_range.end = np.median(poly_a_raw) + 100
    polya_plot._fig.xaxis.axis_label = 'Poly(A) tail length'
    polya_plot._fig.yaxis.axis_label = 'Read count'
    polya_plot._fig.title.text = "Poly(A) tail length estimation"
    subtext = "Histogram showing the distribution of Poly(A) tail lengths for each read, estimated using Dorado."  # noqa: E501
    polya_plot._fig.add_layout(
        Title(text=subtext, text_font_size="0.8em"), 'above')

    return polya_plot
