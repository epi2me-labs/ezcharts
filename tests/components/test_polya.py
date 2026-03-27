"""Test functions in polya module."""
from importlib.resources import files

import numpy as np
import pandas as pd

from ezcharts.components.polya import (
    _calculate_polya_statistics, _generate_histogram_data,
    _get_percent, _interpret_kurtosis_value, format_polya_summary,
    load_polya_metrics,
)


def test_get_percent():
    """Test _get_percent helper function with precise expected values."""
    # Exact calculations
    assert _get_percent(50, 100) == 50.0
    assert _get_percent(25, 100) == 25.0
    assert _get_percent(75, 100) == 75.0
    assert _get_percent(1, 4) == 25.0
    assert _get_percent(3, 4) == 75.0

    # Division by zero case - exact zero
    assert _get_percent(50, 0) == 0.0

    # Edge cases - exact values
    assert _get_percent(0, 100) == 0.0
    assert _get_percent(200, 100) == 200.0  # Can exceed 100%


def test_generate_histogram_data():
    """Test _generate_histogram_data helper function with precise expected values."""
    lengths = [10, 12, 10, 15, 12, 10, 13]
    histogram = _generate_histogram_data(lengths)

    # Should return list of [bin, count] pairs for bins 10 through 15
    assert isinstance(histogram, list)
    assert len(histogram) == 6  # Bins 10, 11, 12, 13, 14, 15

    # Convert to dict for precise checking
    hist_dict = {bin_val: count for bin_val, count in histogram}

    # Exact counts for each bin
    assert hist_dict[10] == 3  # Three 10s in input
    assert hist_dict[11] == 0  # No 11s in input
    assert hist_dict[12] == 2  # Two 12s in input
    assert hist_dict[13] == 1  # One 13 in input
    assert hist_dict[14] == 0  # No 14s in input
    assert hist_dict[15] == 1  # One 15 in input

    # Verify exact range coverage
    bins = [bin_val for bin_val, count in histogram]
    assert min(bins) == 10
    assert max(bins) == 15
    assert bins == [10, 11, 12, 13, 14, 15]

    # Test with empty data - returns [[0, 0]] when no data
    empty_histogram = _generate_histogram_data([])
    assert empty_histogram == [[0, 0]]

    # Test with single value - exact single bin
    single_histogram = _generate_histogram_data([42])
    assert single_histogram == [[42, 1]]

    # Test with identical values - exact single bin with count
    identical_histogram = _generate_histogram_data([7, 7, 7])
    assert identical_histogram == [[7, 3]]


def test_interpret_kurtosis_value():
    """Test _interpret_kurtosis_value helper function with precise inputs."""
    # Exact boundary conditions
    assert (
        _interpret_kurtosis_value(0.6) ==
        "(more outliers compared to normality)"
    )
    assert (
        _interpret_kurtosis_value(0.5) ==
        "(close to normally distributed)"
    )  # Exactly at boundary
    assert (
        _interpret_kurtosis_value(0.51) ==
        "(more outliers compared to normality)"
    )

    assert (
        _interpret_kurtosis_value(-0.6) ==
        "(fewer outliers compared to normality)"
    )
    assert (
        _interpret_kurtosis_value(-0.5) ==
        "(close to normally distributed)"
    )  # Exactly at boundary
    assert (
        _interpret_kurtosis_value(-0.51) ==
        "(fewer outliers compared to normality)"
    )

    # Values within normal range
    assert (
        _interpret_kurtosis_value(0.0) ==
        "(close to normally distributed)"
    )
    assert (
        _interpret_kurtosis_value(0.2) ==
        "(close to normally distributed)"
    )
    assert (
        _interpret_kurtosis_value(-0.2) ==
        "(close to normally distributed)"
    )
    assert (
        _interpret_kurtosis_value(0.49) ==
        "(close to normally distributed)"
    )
    assert (
        _interpret_kurtosis_value(-0.49) ==
        "(close to normally distributed)"
    )

    # NaN case
    assert (
        _interpret_kurtosis_value(np.nan) ==
        ""
    )

    # Extreme values
    assert (
        _interpret_kurtosis_value(10.0) ==
        "(more outliers compared to normality)"
    )
    assert (
        _interpret_kurtosis_value(-10.0) ==
        "(fewer outliers compared to normality)"
    )


def test_load_polya_metrics():
    """Test load_polya_metrics function."""
    bamfile = str(files('ezcharts').joinpath("data/test/polya/RCS-100A.bam"))
    polya_metrics_all_filtered_at_mask = load_polya_metrics(
        bam_file_path=bamfile,
        lower_bound=5,
        upper_bound=15,
        quality_threshold=1000,
        polya_reference_length=10,
        read_length_tolerance_percent=10,
        filter_high_qs=True)
    polya_metrics_plasmid = load_polya_metrics(
        bam_file_path=bamfile,
        lower_bound=5,
        upper_bound=15,
        polya_reference_length=10,
        read_length_tolerance_percent=10)
    polya_metrics_vax = load_polya_metrics(
        bam_file_path=bamfile,
        lower_bound=88,
        upper_bound=132,
        polya_reference_length=100,
        tail_interruption='GCC',
        output_percent_no_tail=True,
        filter_primary=True,
        filter_high_qs=True,
        filter_forward=True,
        filter_has_tail=True,
        filter_len_range=True,
        include_no_tail=True)

    # check polya_metrics_all_filtered_at_mask
    expected_all_filtered_at_mask = {
        'percent_in_bounds': 0.0,
        'total_area':  0.0,
        'area_with':  0.0,
        'percent_polya_area': 0.0,
        'percent_present': 0.0,
        'mean_length': 0.0,
        'median_length': 0.0,
        'std_dev_length':  0.0,
        'kurtosis_length': None,
        'mode_length': 0.0,
        'confidence_interval_length': (0.0, 0.0),
        'lower_bound': 5,
        'upper_bound': 15,
        'reference_length': 10}

    hist = polya_metrics_all_filtered_at_mask['histogram']
    counts = [c for _, c in hist]
    assert sum(counts) == 0
    assert hist[0] == [0, 0]
    assert hist[-1] == [0, 0]
    assert len(hist) == 1
    polya_metrics_all_filtered_at_mask.pop('histogram', None)
    assert polya_metrics_all_filtered_at_mask == expected_all_filtered_at_mask

    # check polya_metrics_plasmid
    expected_polya_metrics_plasmid = {
        'percent_in_bounds': 2.0408163265306123,
        'total_area': 99042,
        'area_with': 99042,
        'percent_polya_area': 100.0,
        'percent_present': 100.0,
        'mean_length': 168.4387755102041,
        'median_length': 119.0,
        'std_dev_length': 104.06447676918496,
        'kurtosis_length': 1.7259187530963596,
        'mode_length': 110.0,
        'confidence_interval_length': (160.01011971630783, 176.86743130410036),
        'lower_bound': 5,
        'upper_bound': 15,
        'reference_length': 10}
    hist = polya_metrics_plasmid['histogram']
    counts = [c for _, c in hist]
    assert sum(counts) == 588
    assert hist[0] == [7, 4]
    assert hist[-1] == [548, 1]
    assert len(hist) == 542
    polya_metrics_plasmid.pop('histogram', None)
    assert polya_metrics_plasmid == expected_polya_metrics_plasmid

    # check polya_metrics_vax
    expected_polya_metrics_vax = {
        'percent_in_bounds': 51.554404145077726,
        'total_area': 67812,
        'area_with': 67015,
        'percent_polya_area': 98.82469179496253,
        'percent_present': 95.59585492227978,
        'mean_length': 175.67875647668393,
        'median_length': 123.0,
        'std_dev_length': 109.32912500113851,
        'kurtosis_length': 1.2186277723463137,
        'mode_length': 109.0,
        'confidence_interval_length':  (164.737738735267, 186.61977421810087),
        'lower_bound': 88,
        'upper_bound': 132,
        'percent_no_tail': 39.25619834710744,
        'reference_length': 100,
        'tail_interruption': 'GCC'}
    hist = polya_metrics_vax['histogram']
    counts = [c for _, c in hist]
    assert sum(counts) == 386
    assert hist[0] == [7, 2]
    assert hist[-1] == [548, 1]
    assert len(hist) == 542
    polya_metrics_vax.pop('histogram', None)
    assert polya_metrics_vax == expected_polya_metrics_vax


def test_calculate_polya_statistics():
    """Test _calculate_polya_statistics function."""
    # Test with known data: [80, 85, 90, 95, 100, 105, 110, 115, 120]
    lengths = pd.Series([80, 85, 90, 95, 100, 105, 110, 115, 120])
    lower_bound = 90
    upper_bound = 110

    stats = _calculate_polya_statistics(lengths, lower_bound, upper_bound)

    # Check that all required keys are present
    required_keys = [
        'histogram', 'percent_in_bounds', 'total_area', 'area_with',
        'percent_polya_area', 'percent_present', 'mean_length',
        'median_length', 'std_dev_length', 'kurtosis_length',
        'mode_length', 'confidence_interval_length'
    ]

    for key in required_keys:
        assert key in stats

    # Precise calculations with known input [80, 85, 90, 95, 100, 105, 110, 115, 120]
    assert stats['mean_length'] == 100.0  # Sum: 900, Count: 9, Mean: 100.0
    assert stats['median_length'] == 100.0  # Middle value of 9 elements
    assert stats['total_area'] == 900  # Sum of all values

    # In bounds: [90, 95, 100, 105, 110] = 5 out of 9 values
    assert stats['percent_in_bounds'] == (5/9) * 100  # 55.555...

    # With poly(A) (>= 90): [90, 95, 100, 105, 110, 115, 120] = 7/9 values
    assert stats['percent_present'] == (7/9) * 100  # 77.777...

    # Area with poly(A): 90+95+100+105+110+115+120 = 735
    assert stats['area_with'] == 735
    assert stats['percent_polya_area'] == (735/900) * 100  # 81.666...

    # Standard deviation calculation for [80, 85, 90, 95, 100, 105, 110, 115, 120]
    # Using ddof=1 (sample std dev): sqrt(sum((x-mean)^2)/(n-1))
    expected_std = 13.693063937629153
    assert abs(stats['std_dev_length'] - expected_std) < 1e-10

    # Test with empty data - exact zero values
    empty_stats = _calculate_polya_statistics(pd.Series(dtype=float), 80, 120)
    for key in required_keys:
        assert key in empty_stats
    assert empty_stats['histogram'] == [[0, 0]]
    assert empty_stats['mean_length'] == 0.0
    assert empty_stats['total_area'] == 0.0
    assert empty_stats['percent_in_bounds'] == 0.0
    assert empty_stats['percent_present'] == 0.0


def test_format_polya_summary():
    """Test format_polya_summary function."""
    # Create sample metrics with known values
    metrics = {
        'reference_length': 100,
        'median_length': 95.5,
        'mean_length': 98.2,
        'confidence_interval_length': (92.1, 104.3),
        'mode_length': 90.0,
        'percent_present': 85.5,
        'lower_bound': 80,
        'upper_bound': 120,
        'percent_in_bounds': 75.8,
        'percent_no_tail': 14.5,
        'kurtosis_length': 0.8,
        'tail_interruption': 'GCC',
        'histogram': [[95, 5], [98, 10], [100, 8]]
    }

    summary = format_polya_summary(metrics)

    # Check that all expected keys are present
    expected_keys = [
        'Reference length', 'Median length', 'Mean (95% CI)', 'Mode',
        'Percent Poly(A)', 'Percent in length bounds',
        'Percent reads no Poly(A)', 'Kurtosis deviation from normality',
        'Tail interruption'
    ]

    for key in expected_keys:
        assert key in summary

    # Check formatted values
    assert summary['Reference length'] == '100b'
    assert summary['Median length'] == 95.5
    assert summary['Mean (95% CI)'] == '(92.1) 98.2 (104.3)'
    assert summary['Mode'] == 90.0
    assert summary['Percent Poly(A)'] == 85.5
    assert summary['Percent in length bounds'] == '(80) 75.8 (120)'
    assert summary['Percent reads no Poly(A)'] == 14.5
    assert (
        summary['Kurtosis deviation from normality'] ==
        '0.8 (more outliers compared to normality)'
    )
    assert summary['Tail interruption'] == 'GCC'

    # Test with different kurtosis values
    metrics_low_kurt = metrics.copy()
    metrics_low_kurt['kurtosis_length'] = -0.8
    summary_low = format_polya_summary(metrics_low_kurt)
    assert (
        summary_low['Kurtosis deviation from normality'] ==
        '-0.8 (fewer outliers compared to normality)'
    )

    metrics_normal_kurt = metrics.copy()
    metrics_normal_kurt['kurtosis_length'] = 0.2
    summary_normal = format_polya_summary(metrics_normal_kurt)
    assert (
        summary_normal['Kurtosis deviation from normality'] ==
        '0.2 (close to normally distributed)'
    )

    # test single read CI suppression
    metrics_single_read = metrics.copy()
    metrics_single_read['histogram'] = [[98, 1]]  # single read
    summary_single = format_polya_summary(metrics_single_read)
    assert 'Mean' in summary_single
    assert 'Mean (95% CI)' not in summary_single
    assert summary_single['Mean'] == '98.2'
