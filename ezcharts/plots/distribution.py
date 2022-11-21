"""Distributional plots."""

import numpy as np
from seaborn._statistics import Histogram

from ezcharts.plots import Plot


__all__ = ["displot", "histplot", "kdeplot", "ecdfplot", "rugplot", "distplot"]


def displot(*args, **kwargs):
    """Figure-level interface for distribution plots in a grid."""
    raise NotImplementedError


def histplot(
    data=None, *, x=None, y=None, hue=None, weights=None,
    stat='count', bins='auto', binwidth=None, binrange=None,
    discrete=None, cumulative=False, common_bins=True,
    common_norm=True, multiple='layer', element='bars',
    fill=True, shrink=1, kde=False, kde_kws=None,
    line_kws=None, thresh=0, pthresh=None, pmax=None,
    cbar=False, cbar_ax=None, cbar_kws=None, palette=None,
    hue_order=None, hue_norm=None, color=None, log_scale=None,
        legend=True, ax=None, **kwargs):
    """Plot univariate or bivariate histograms to show distributions."""
    estimate_kws = dict(
        stat=stat,
        bins=bins,
        binwidth=binwidth,
        binrange=binrange,
        discrete=discrete,
        cumulative=cumulative,
    )
    estimator = Histogram(**estimate_kws)
    heights, edges = estimator(data, weights=weights)

    # WARNING: The bars are centered on the ticks. Add half a bin width to the
    # edges to left-align them with the bin start tick.
    binwidth = binwidth if binwidth else edges[1] - edges[0]

    edges_right_shifted = edges + binwidth / 2

    heights = np.append(heights, 0)
    data = np.column_stack([edges_right_shifted, heights]).tolist()

    plt = Plot()

    plt.xAxis = dict(type='value', scale=True)
    plt.yAxis = dict()
    plt.dataset = [dict(source=data)]

    plt.series = [dict(
        name='histogram', type='bar', barWidth='100%', datasetIndex=0)]

    plt.xAxis.min = edges.min()
    plt.xAxis.max = np.ceil(edges_right_shifted.max())

    return plt


def kdeplot(*args, **kwargs):
    """Plot uni/bi-variate distributions using kernel density estimation."""
    raise NotImplementedError


def ecdfplot(*args, **kwargs):
    """Plot empirical cumulative distribution functions."""
    raise NotImplementedError


def rugplot(*args, **kwargs):
    """Plot marginal distributions by drawing ticks along the x and y axes."""
    raise NotImplementedError


def distplot(*args, **kwargs):
    """Flexibly plot a univariate distribution of observations (DEPRECATED)."""
    raise DeprecationWarning
    raise NotImplementedError
