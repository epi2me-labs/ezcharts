"""Utility functions for aiding plotting."""

import json
import logging

import numpy as np
import pandas as pd
import pkg_resources
from scipy import stats as sp_stats

from ezcharts.plots.prodict import Prodict


sns_type_to_echarts = {
    "categorical": "category",
    "numeric": "value"}


class MagicObject(Prodict):
    """Nothing to see here."""

    def __getattr__(self, attr):
        """Get attribute, setting to default value if not preexisting.

        If the attribite is a known annotation, the corresponding
        constructor will be used, else a generic MagicObject will be
        created.
        """
        try:
            return self[attr]
        except KeyError:
            if self.has_attr(attr):
                construct = self.attr_type(attr)
            else:
                construct = MagicObject
            setattr(self, attr, construct())
            return super().__getattr__(attr)

    def to_json(self, **kwargs):
        """Create json represention for echarts."""
        return json.dumps(self, **kwargs)


def get_named_logger(name):
    """Create a logger with a name.

    :param name: name of logger.
    """
    name = name.ljust(10)[:10]  # so logging is aligned
    logger = logging.getLogger('{}.{}'.format(__package__, name))
    logger.name = name
    return logger


def set_basic_logging(level=logging.INFO):
    """Set basic log formatting.

    :returns: logger instance.
    """
    logging.basicConfig(
        format='[%(asctime)s - %(name)s] %(message)s',
        datefmt='%H:%M:%S', level=level)
    logger = logging.getLogger(__package__)
    logger.setLevel(level)
    return logger


def read_files(summaries):
    """Read a set of files and join to single dataframe."""
    dfs = list()
    if not isinstance(summaries, (list, tuple)):
        summaries = [summaries]
    for fname in sorted(summaries):
        dfs.append(pd.read_csv(fname, sep="\t"))
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


def choose_palette(ncolours):
    """Choose colour palette.

    :param: ncolours: number of colours.
    """
    raise NotImplementedError


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
        logger = get_named_logger('PlotWrap')
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