"""Test functions in utils."""

from contextlib import contextmanager
import os
import tempfile

import pandas as pd
from pkg_resources import resource_filename
import pytest

from ezcharts.components import fastcat


def _read_pandas(fname, dtype, target_cols=None):
    # this is a blind reimplementation that handles all file types
    # and simply in order to make this not just the module code

    flagstat = set(dtype.keys()) == set(fastcat.BAMSTATS_FLAGSTAT_COLS_DTYPES.keys())
    kwargs = dict()

    if not flagstat:
        kwargs["parse_dates"] = ["start_time"]
    df = pd.read_csv(
        fname, sep="\t", usecols=dtype.keys(), dtype=dtype, **kwargs
    ).reset_index(drop=True)

    if flagstat:
        df["status"] = df["ref"].apply(lambda x: "Unmapped" if x == "*" else "Mapped")
    else:
        df["start_time"] = pd.to_datetime(df.start_time, utc=True).dt.tz_localize(None)

    # homogenise fastcat and bamstats names
    df.rename(columns={"name": "read_id"}, inplace=True)

    if target_cols is not None:
        df = df[target_cols]
    return df


def _read_histograms(hist_metric, dtypes):
    hist = pd.read_csv(
        hist_metric, sep="\t", names=["start", "end", "count"], dtype=dtypes
    )
    return hist


def _compare_frames(actual, expected):
    pd.testing.assert_frame_equal(
        actual,
        expected,
        check_dtype=True,
        check_categorical=True,
        check_exact=True,
        check_datetimelike_compat=True,
    )


@contextmanager
def _empty_file(dtype=None):
    """Create an emtpy file or just with the headers."""
    with tempfile.NamedTemporaryFile(mode="r+", suffix=".tsv") as fname:
        if dtype:
            empty_df = pd.DataFrame(columns=dtype)
            empty_df.to_csv(fname.name, sep="\t")
        yield fname.name


def _multisamples():
    samples = ["S1", "S2", "S3"]
    files = [_empty_file() for i in samples]
    return samples, files


def test_001_read_fastcat():
    """Reading a fastcat file."""
    fname = resource_filename(
        "ezcharts", "data/test/real_data_test/fastcat/barcode01/per-read-stats.tsv.gz"
    )
    actual = fastcat.load_fastcat(fname)
    expected = _read_pandas(fname, fastcat.FASTCAT_COLS_DTYPES)
    _compare_frames(actual, expected)


def test_002_read_fastcat_subset():
    """Reading a fastcat with a subset of columns."""
    fname = resource_filename(
        "ezcharts", "data/test/real_data_test/fastcat/barcode01/per-read-stats.tsv.gz"
    )
    target_cols = ["sample_name", "read_length", "mean_quality"]
    for i in range(1, 3):
        actual = fastcat.load_bamstats(fname, target_cols=target_cols[:i])
        expected = _read_pandas(
            fname, fastcat.FASTCAT_COLS_DTYPES, target_cols=target_cols[:i]
        )
        _compare_frames(expected, actual)


def test_004_fastcat_just_headers():
    """Can read a file with no records."""
    with _empty_file(dtype=fastcat.FASTCAT_COLS_DTYPES) as fname:
        actual = fastcat.load_fastcat(fname).reset_index(drop=True)
        expected = _read_pandas(fname, fastcat.FASTCAT_COLS_DTYPES)
        _compare_frames(actual, expected)


def test_005_fastcat_empty():
    """Should raise an error if file completely empty."""
    with _empty_file() as fname:
        with pytest.raises(Exception, match=f"Empty input: {fname}"):
            fastcat.load_fastcat(fname)


def test_011_read_bamstats():
    """Reading a bamstats file."""
    fname = resource_filename(
        "ezcharts",
        "data/test/real_data_test/bamstats/barcode01/bamstats.readstats.tsv.gz",
    )
    actual = fastcat.load_bamstats(fname)
    expected = _read_pandas(fname, fastcat.BAMSTATS_COLS_DTYPES)
    _compare_frames(expected, actual)


def test_012_read_bamstats_subset():
    """Reading a bamstats with a subset of columns."""
    fname = resource_filename(
        "ezcharts",
        "data/test/real_data_test/bamstats/barcode01/bamstats.readstats.tsv.gz",
    )
    target_cols = ["sample_name", "read_length", "mean_quality"]
    for i in range(1, 3):
        actual = fastcat.load_bamstats(fname, target_cols=target_cols[0:i])
        expected = _read_pandas(
            fname, fastcat.BAMSTATS_COLS_DTYPES, target_cols=target_cols[:i]
        )
        _compare_frames(expected, actual)


def test_014_bamstats_just_headers():
    """Can read a file with no records."""
    with _empty_file(dtype=fastcat.BAMSTATS_COLS_DTYPES.keys()) as fname:
        actual = fastcat.load_bamstats(fname).reset_index(drop=True)
        expected = _read_pandas(fname, fastcat.BAMSTATS_COLS_DTYPES)
        _compare_frames(actual, expected)


def test_015_bamstats_empty():
    """Should raise an error if file completely empty."""
    with _empty_file() as fname:
        with pytest.raises(Exception, match=f"Empty input: {fname}"):
            fastcat.load_bamstats(fname)


def test_021_read_either():
    """Auto-detect file type and read."""
    per_read_stats_fastcat = resource_filename(
        "ezcharts", "data/test/real_data_test/fastcat/barcode01/per-read-stats.tsv.gz"
    )
    per_read_stats_bamstats = resource_filename(
        "ezcharts",
        "data/test/real_data_test/bamstats/barcode01/bamstats.readstats.tsv.gz",
    )
    target_cols_fastcat = ["sample_name", "read_length", "mean_quality"]
    target_cols_bamstats = [
        "sample_name", "coverage", "read_length", "mean_quality", "acc"]
    to_test = (
        (per_read_stats_fastcat, fastcat.FASTCAT_COLS_DTYPES, target_cols_fastcat),
        (per_read_stats_bamstats, fastcat.BAMSTATS_COLS_DTYPES, target_cols_bamstats),
    )
    for fname, TYPE, target_cols in to_test:
        actual = fastcat.load_stats(fname)
        expected = _read_pandas(fname, TYPE, target_cols=target_cols)
        _compare_frames(actual, expected)


def test_025_equality_of_result():
    """Return a consistent data structure."""
    per_read_stats_fastcat = resource_filename(
        "ezcharts", "data/test/real_data_test/fastcat/barcode01/per-read-stats.tsv.gz"
    )
    per_read_stats_bamstats = resource_filename(
        "ezcharts",
        "data/test/real_data_test/bamstats/barcode01/bamstats.readstats.tsv.gz",
    )
    target_cols = ["sample_name", "read_length", "mean_quality"]
    actual_fastcat = (
        fastcat.load_stats(per_read_stats_fastcat, target_cols=target_cols)
        .sort_values(["read_length", "mean_quality"])
        .reset_index(drop=True)
    )
    actual_bamstats = (
        fastcat.load_stats(per_read_stats_bamstats, target_cols=target_cols)
        .sort_values(["read_length", "mean_quality"])
        .reset_index(drop=True)
    )
    _compare_frames(actual_fastcat, actual_bamstats)


def test_031_read_flagstat():
    """Read a flagstats file."""
    fname = resource_filename("ezcharts", "data/test/bamstats.flagstat.tsv")
    actual = fastcat.load_bamstats_flagstat(fname)
    expected = _read_pandas(fname, fastcat.BAMSTATS_FLAGSTAT_COLS_DTYPES)
    _compare_frames(actual, expected)


def test_034_read_flagstat_just_headers():
    """Can read a file with no records."""
    with _empty_file(dtype=fastcat.BAMSTATS_FLAGSTAT_COLS_DTYPES.keys()) as fname:
        actual = fastcat.load_bamstats_flagstat(fname).reset_index(drop=True)
        expected = _read_pandas(fname, fastcat.BAMSTATS_FLAGSTAT_COLS_DTYPES)
        _compare_frames(actual, expected)


def test_035_read_flagstat_empty():
    """Should raise an error if file completely empty."""
    with _empty_file() as fname:
        with pytest.raises(Exception, match=f"Empty input: {fname}"):
            fastcat.load_bamstats_flagstat(fname)


def test_041_load_histogram():
    """Test load histogram."""
    # TODO: test histograms from bamstats
    hist_dir = resource_filename(
        "ezcharts",
        "data/test/real_data_test/bamstats/barcode01/",
    )
    variables = {
        "quality",
        "length",
        "quality.unmap",
        "length.unmap",
        "accuracy",
        "coverage",
    }
    for v in variables:
        actual = fastcat.load_histogram(hist_dir, v)
        if "length" in v:
            cols = {"start": int, "end": int, "count": int}
        else:
            cols = {"start": float, "end": float, "count": int}
        expected = _read_histograms(os.path.join(hist_dir, f"{v}.hist"), dtypes=cols)
        _compare_frames(actual, expected)


def test_042_load_unallowed_histogram():
    """Load an unallowed type."""
    hist_dir = resource_filename(
        "ezcharts",
        "data/test/real_data_test/fastcat/barcode01/",
    )
    with pytest.raises(ValueError, match=r"^`dtype` must be one of"):
        fastcat.load_histogram(hist_dir, "unallowed")


def test_101_multi_sample():
    """Raise an error if there is a discordance between number of samples and files."""
    # Create a couple of samples
    samples, files = _multisamples()
    with pytest.raises(
        ValueError,
        match="`sample_names` must be provided as a tuple "
        + "when more than one input provided.",
    ):
        # pass just first sample
        fastcat.SeqSummary(seq_summary=tuple(files), sample_names=samples[0])


def test_102_discordance_samples_files():
    """Raise an error if there is a discordance between number of samples and files."""
    # Create a couple of samples
    samples, files = _multisamples()
    with pytest.raises(
        ValueError,
        match="`sample_names` must have the same length ",
    ):
        # pass one sample less than number of files.
        fastcat.SeqSummary(seq_summary=tuple(files), sample_names=tuple(samples[:-1]))


def test_103_pass_lists():
    """Raise an error if not expected input structures are passed."""
    # Create a couple of samples
    samples, files = _multisamples()
    with pytest.raises(
        ValueError,
        match="`seq_summary` must be a path to a fastcat/bamstats ",
    ):
        # pass one sample less than number of files.
        fastcat.SeqSummary(seq_summary=files, sample_names=samples[:-1])


@pytest.mark.parametrize(
    "input",
    [
        "data/test/fastcat/f1.tsv.gz",  # file
        "data/test/histogram_stats/sample_1",  # fastcat histograms
        [  # more than 1 sample
            "data/test/fastcat/f1.tsv.gz",
            "data/test/fastcat/f2.tsv.gz",
        ],
        [  # more than 1 sample from histograms
            "data/test/histogram_stats/sample_1",
            "data/test/histogram_stats/sample_2",
        ],
    ],
)
def test_104_SeqSummary(input):
    """Create the SeqSummary component with various inputs."""
    if not isinstance(input, list):
        fastcat.SeqSummary(seq_summary=resource_filename("ezcharts", input))
    else:
        fastcat.SeqSummary(
            seq_summary=tuple([resource_filename("ezcharts", i) for i in input]),
            sample_names=tuple(["S" + i for i in input]),
        )


def test_105_bamstats_inputs():
    """Test if SeqSummary works with bam_flagstat inputs."""
    # Create a couple of samples
    seq_summary = resource_filename(
        "ezcharts",
        "data/test/real_data_test/bamstats/barcode01/bamstats.readstats.tsv.gz"
    )
    flagstats = resource_filename(
        "ezcharts",
        "data/test/real_data_test/bamstats/barcode01/bamstats.flagstat.tsv"
    )
    # pass just first sample
    fastcat.SeqSummary(
        seq_summary=seq_summary,
        sample_names="barcode01",
        flagstat=flagstats)


def test_106_multi_sample_by_metric():
    """Test if SeqCompare works."""
    # Create a couple of samples
    samples, files = _multisamples()
    with pytest.raises(
        ValueError,
        match="`sample_names` must be provided as a tuple "
        + "when more than one input provided.",
    ):
        # pass just first sample
        fastcat.SeqCompare(
            seq_summary=tuple(files), sample_names=samples[0])


def test_107_SeqSummary_empty_file():
    """Create the SeqSummary component with an empty file (summaries)."""
    with _empty_file(dtype=fastcat.FASTCAT_COLS_DTYPES) as fname:
        fastcat.SeqSummary(seq_summary=fname)


def test_108_SeqSummary_empty_histogram_files():
    """Create the SeqSummary component with an histograms dir with empty files."""
    fastcat.SeqSummary(
        seq_summary=resource_filename(
            "ezcharts", "data/test/histogram_stats/empty_sample/"
        )
    )
