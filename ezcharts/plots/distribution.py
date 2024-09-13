"""Distributional plots."""
from itertools import cycle

from bokeh.models import HoverTool
import pandas as pd
from seaborn._statistics import Histogram

from ezcharts.plots import BokehPlot, util


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
        legend=True, ax=None, **quad_kwargs):
    """Plot univariate or multivariate histograms."""
    plt = BokehPlot()

    estimate_kws = dict(
        stat=stat,
        bins=bins,
        binwidth=binwidth,
        binrange=binrange,
        discrete=discrete,
        cumulative=cumulative,
    )
    data = pd.DataFrame(data)

    estimator = Histogram(**estimate_kws)

    if data.ndim > 1 and data.shape[1] > 1:
        # multivariate data
        opacity = 0.5
        if palette is None:
            palette = util.choose_palette()
    else:
        opacity = 1.0
        if color is None:
            palette = util.choose_palette()
        else:
            palette = [color]
    if hue:
        data = data.pivot(columns=hue, values=data.columns[0])
    # this just looks over values if data is 1D
    # for var, color in zip(data, cycle(palette)):
    for col, color in zip(data.columns, cycle(palette)):
        quad_kwargs = {}
        if len(data.columns) > 1:
            quad_kwargs["legend_label"] = col
        variable_data = data[col].dropna()
        heights, edges = estimator(variable_data, weights=weights)

        plt._fig.quad(
            top=heights, bottom=0, left=edges[:-1], right=edges[1:],
            fill_color=color, fill_alpha=opacity, line_color=color, **quad_kwargs
        )
    plt._fig.y_range.start = 0
    hover = plt._fig.select(dict(type=HoverTool))
    hover.tooltips = [(stat.capitalize(), "@top")]
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
