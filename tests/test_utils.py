"""Test functions in utils."""

import argparse
import logging

import pandas as pd

from ezcharts import util
from ezcharts.plots.util import concat_dfs_with_categorical_columns


def test_create_logger():
    """Make a logger."""
    logger = util.get_named_logger("MyLogger")
    assert isinstance(logger, logging.Logger)


def test_set_log_level():
    """Make a parser."""
    parser = util._log_level()
    assert isinstance(parser, argparse.ArgumentParser)


def test_010_pandas_cat_properties():
    """Ensure concatenating categoricals works as intended."""
    # Input columns for fastcat
    example_cols_dtypes = {
        "string": str,
        "int": int,
        "bi_category": "category",  # all the dfs contains these categories: F,M
        "open_category": "category",  # categories aren't in all the dfs: filename
        "float": float,
        # "datetime": pd.Timestamp('20240310')
    }
    d1 = {
        "string": ['rA', 'rB', 'rC'],
        "int": [1000, 2000, 1500],
        "bi_category": ['B', 'A', 'B'],
        "open_category": ['C', 'A', 'C'],
        "float": [3.1, 9.9, 4.9]
    }
    df1 = pd.DataFrame(d1).astype(example_cols_dtypes)
    d2 = {
        "string": ['rA_2', 'rB_2', 'rC_2'],
        "int": [2000, 1000, 5000],
        "bi_category": ['A', 'A', 'A'],
        "open_category": ['B', 'A', 'B'],  # 'B' is not present in df1
        "float": [4.9, 9.9, 3.1]
    }
    df2 = pd.DataFrame(d2).astype(example_cols_dtypes)
    df_empty = pd.DataFrame(
        columns=example_cols_dtypes.keys()
        ).astype(example_cols_dtypes)

    actual = concat_dfs_with_categorical_columns(dfs=[df1, df2, df_empty])
    expected_d = {
        k1: d1[k1] + d2[k2]
        for (k1, k2) in zip(d1.keys(), d2.keys())}
    expected = pd.DataFrame(expected_d).astype(example_cols_dtypes)
    pd.testing.assert_frame_equal(
        expected, actual,
        check_dtype=True, check_categorical=True, check_exact=True
    )
