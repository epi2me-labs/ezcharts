"""Utility functions for aiding plotting."""
from itertools import cycle, islice

import numpy as np
import pandas as pd
import pkg_resources
from scipy import stats as sp_stats

from ezcharts import util

sns_type_to_echarts = {
    "categorical": "category",
    "numeric": "value"}


class JSCode():
    """A class for javascript code snippets."""

    DELIMITER = "~~~0^0~~~"

    def __init__(self, jscode):
        """Initialise object."""
        self.jscode = jscode

    def to_json(self):
        """Output json with some stuff so we can strip them out."""
        return f"{self.DELIMITER}{self.jscode}{self.DELIMITER}"

    @classmethod
    def _clean(cls, jscode):
        """
        Clean up escape characters in the code.

        This method is intended for use after JSON serialisation.
        """
        dirty = [
            '"%s' % cls.DELIMITER,
            '%s"' % cls.DELIMITER,
            "\\n"]

        for find in dirty:
            jscode = jscode.replace(find, '')

        return jscode


def read_files(summaries, sep="\t"):
    """Read a set of files and join to single dataframe."""
    dfs = list()
    if not isinstance(summaries, (list, tuple)):
        summaries = [summaries]
    for fname in sorted(summaries):
        dfs.append(pd.read_csv(fname, sep=sep))
    return pd.concat(dfs)


class _colors:
    """Some colours that someone thought were nice."""

    cerulean = "#0084A9"
    not_black = "#001A21"
    feldgrau = "#455556"
    dim_gray = "#666666"
    light_cornflower_blue = "#90C5E7"
    dark_gray = "#B5AEA7"
    isabelline = "#F0EFED"
    medium_spring_bud = "#B8E986"
    cinnabar = "#EF4134"
    sandstorm = "#F5CC49"
    fandango = "#A53F96"
    green = "#17BB75"
    verdigris = "#54B8B1"

    white = "#FFFFFF"
    black = "#000000"
    grey10 = "#1A1A1A"
    grey20 = "#333333"
    grey30 = "#4D4D4D"
    grey40 = "#666666"
    grey50 = "#808080"
    grey60 = "#999999"
    grey70 = "#B3B3B3"
    grey80 = "#CCCCCC"
    grey90 = "#E6E6E6"


class _ontColors:
    """ONT Brand colors."""

    BRAND_BLUE = '#0084A9'
    BRAND_BLUE_LIGHT = '#0084a91a'
    BRAND_LIGHT_BLUE = '#90C6E7'
    BRAND_BLACK = '#333333'
    BRAND_LIGHT_GREY = '#B5AEA7'
    BRAND_GREY = '#666666'
    BRAND_GREY_LIGHT = '#6666661f'

    BRAND_LOGO = pkg_resources.resource_filename(
        'ezcharts', 'data/images/ONT_logo.txt')
    with open(BRAND_LOGO, 'r', encoding="UTF-8") as fh:
        BRAND_LOGO = fh.read()


class _ondColors:
    """OND Brand colors."""

    BRAND_BLUE = '#003E71'
    BRAND_BLUE_LIGHT = '#003e7136'
    BRAND_LIGHT_BLUE = '#90C6E7'
    BRAND_BLACK = '#333333'
    BRAND_LIGHT_GREY = '#B5AEA7'
    BRAND_GREY = '#666666'
    BRAND_GREY_LIGHT = '#6666661f'
    BRAND_RED = '#f45b69'

    BRAND_LOGO = pkg_resources.resource_filename(
        'ezcharts', 'data/images/OND_logo.txt')
    with open(BRAND_LOGO, 'r', encoding="UTF-8") as fh:
        BRAND_LOGO = fh.read()


Colors = _colors()
ont_colors = _ontColors()
ond_colors = _ondColors()


def kernel_density_estimate(x, step=0.2):
    """Kernel density to approximate distribution.

    :param x: data of which to find mode.
    :param step: discretization of KDE PDF.
    """
    # estimate bandwidth of kde, R's nrd0 rule-of-thumb
    hi = np.std(x, ddof=1)
    q75, q25 = np.percentile(x, [75, 25])
    iqr = q75 - q25
    lo = min(hi, iqr/1.34)
    if not ((lo == hi) or (lo == abs(x[0])) or (lo == 1)):
        lo = 1
    bw = 0.9 * lo * len(x)**-0.2

    # create a KDE
    x_grid = np.arange(min(x), max(x), step)
    kernel = sp_stats.gaussian_kde(x, bw_method=bw)
    pdf = kernel(x_grid)
    return x_grid, pdf


def choose_palette(name='colorblind', ncolours=None):
    """Choose colour palette.

    These are seaborn's qualitative color palettes.
    https://seaborn.pydata.org/tutorial/color_palettes.html

    :param: name: name of palette to return colors from.
    :param: ncolours: number of colours.
    """
    palettes = {
        'colorblind': [
            '#0173b2', '#de8f05', '#029e73', '#d55e00', '#cc78bc',
            '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9'],
        'deep': [
            '#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3',
            '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd'],
        'dark': [
            '#001c7f', '#b1400d', '#12711c', '#8c0800', '#591e71',
            '#592f0d', '#a23582', '#3c3c3c', '#b8850a', '#006374'],
        'muted': [
            '#4878d0', '#ee854a', '#6acc64', '#d65f5f', '#956cb4',
            '#8c613c', '#dc7ec0', '#797979', '#d5bb67', '#82c6e2'],
        'bright': [
            '#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2',
            '#9f4800', '#f14cc1', '#a3a3a3', '#ffc400', '#00d7ff'],
        'pastel': [
            '#a1c9f4', '#ffb482', '#8de5a1', '#ff9f9b', '#d0bbff',
            '#debb9b', '#fab0e4', '#cfcfcf', '#fffea3', '#b9f2f0'],
        # Uniform palettes
        'rocket': [
            '#35193e', '#701f57', '#ad1759', '#e13342', '#f37651',
            '#f6b48f'],
        'mako': [
            '#2e1e3b', '#413d7b', '#37659e', '#348fa7', '#40b7ad',
            '#8bdab2'],
        'flare': [
            '#e98d6b', '#e3685c', '#d14a61', '#b13c6c', '#8f3371',
            '#6c2b6d'],
        'crest': [
            '#7dba91', '#59a590', '#40908e', '#287a8c', '#1c6488',
            '#254b7f'],
        'magma': [
            '#221150', '#5f187f', '#982d80', '#d3436e', '#f8765c',
            '#febb81'],
        'viridis': [
            '#46327e', '#365c8d', '#277f8e', '#1fa187', '#4ac16d',
            '#a0da39'],
        'rocket_r': [
            '#f6b48f', '#f37651', '#e13342', '#ad1759', '#701f57',
            '#35193e'],
        # Uniform diverging palettes
        'vlag': [
            '#6e90bf', '#aab8d0', '#e4e5eb', '#f2dfdd', '#d9a6a4',
            '#c26f6d'],
        'icefire': [
            '#55a3cd', '#4954b0', '#282739', '#3b2127', '#9c2f45',
            '#e96f36']
    }

    if ncolours is None:
        return palettes[name]

    cycler = cycle(palettes[name])
    return [c for c in islice(cycler, ncolours)]


def emptyPlot(**kwargs):
    """Empty plot for when all else fails.

    :param kwargs: kwargs for bokeh figure.

    :returns: a bokeh plot.
    """
    raise NotImplementedError


def plot_wrapper(func):
    """Test for function and output empty graph if fails.

    :param func:  name of plotting function from aplanat.
    :param args: the arguments provided.
    :param kwargs: other optional key word arguments.

    :returns: plot.

    """
    def wrapper_accepting_arguments(*args, **kwargs):
        """Argument wrapper for decorator."""
        logger = util.get_named_logger('PlotWrap')
        try:
            p = (func(*args, **kwargs))
            return p
        except Exception as e:

            try:
                p = emptyPlot(**kwargs)
                logger.exception('Plotting user plot failed with: '+str(e))
                return p

            except Exception as f:
                p = emptyPlot()
                logger.exception(
                    'Plotting templated Empty plot failed with: ' + str(f))
                return p

    return wrapper_accepting_arguments
