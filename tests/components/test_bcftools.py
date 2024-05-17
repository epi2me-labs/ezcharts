"""Test functions in utils."""

from pkg_resources import resource_filename
import pytest

from ezcharts.components import bcfstats


@pytest.mark.parametrize(
    "fname, expected_idd_empty", [
        ("data/test/bcftools/variants.stats", False),
        ("data/test/bcftools/cw-3767-variants.stats", True)
    ])
def test_001_read_bcfstats(fname, expected_idd_empty):
    """Reading a bcfstats file and checking contents."""
    fpath = resource_filename("ezcharts", fname)
    parsed_data = bcfstats.parse_bcftools_stats(fpath)

    # Check that 'IDD' key exists in parsed_data
    assert "IDD" in parsed_data

    # Check if 'IDD' is a dataframe and verify its content based on expected_idd_empty
    idd = parsed_data["IDD"]
    assert hasattr(idd, "empty")

    if expected_idd_empty:
        assert idd.empty
    else:
        assert not idd.empty
