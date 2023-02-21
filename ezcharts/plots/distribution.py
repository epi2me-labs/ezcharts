"""Distributional plots."""

import numpy as np
import pandas as pd
from seaborn._statistics import Histogram

from ezcharts.plots import _HistogramPlot, util


__all__ = ["displot", "histplot", "kdeplot", "ecdfplot", "rugplot", "distplot"]


def displot(*args, **kwargs):
    """Figure-level interface for distribution plots in a grid."""
    raise NotImplementedError


class MakeRectangles(util.JSCode):
    """
    Make JSCode rectangles.

    Use Instance as an argument to series.renderItem.
    Series.encode should list two x dimensions for bar start and end
    and one y dimension for bar height.
    """

    def __init__(self):
        """Instantiate the class with some jscode.

        Each call to this function creates JS code to make a single echarts
        rectangle.

        First get the x-start, x-end and height of the rectangle in raw data
        coords. eg: var data_x_start = api.value(0);

        Convert the raw data coords to canvas coords.
        Note in canvas coords (x=0, y=0) is in the top left.
        eg: var start = api.coord([data_start, 0]);

        start[1] is y=0 in canvas coords. Subtract the height from this to get
        the canvas coords for the top of the rectangle.
        """
        jscode = """function renderItem(params, api) {
            var data_x_start = api.value(0);
            var data_x_end = api.value(1);
            var data_height = api.value(2);

            var start = api.coord([data_x_start, 0]);
            var end = api.coord([data_x_end, 0]);
            var height = api.size([0, data_height])[1];

            var rectShape = echarts.graphic.clipRectByRect(
                {
                    x: start[0],
                    y: start[1] - height,
                    width: end[0] - start[0],
                    height: height
                },
                {
                    x: params.coordSys.x,
                    y: params.coordSys.y,
                    width: params.coordSys.width,
                    height: params.coordSys.height
                }
            );
            return (
                rectShape && {
                    type: 'rect',
                    transition: ['shape'],
                    shape: rectShape,
                    style: api.style()

                }
            );}"""

        super().__init__(jscode)


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
    """Plot univariate or multivariate histograms."""
    plt = _HistogramPlot()
    plt.xAxis = dict()
    plt.yAxis = dict()

    estimate_kws = dict(
        stat=stat,
        bins=bins,
        binwidth=binwidth,
        binrange=binrange,
        discrete=discrete,
        cumulative=cumulative,
    )

    data = pd.DataFrame(data)

    if data.shape[1] > 1:
        # multivariate data
        opacity = 0.5
        if palette is None:
            palette = util.choose_palette(ncolours=data.shape[1])
    else:
        opacity = 1.0
        if color is None:
            palette = util.choose_palette(ncolours=1)
        else:
            palette = [color]

    if hue:
        data = data.pivot(columns=hue, values=data.columns[0])

    for dataset_idx, col in enumerate(data.columns):
        variable_data = data[col].dropna()
        estimator = Histogram(**estimate_kws)
        heights, edges = estimator(variable_data, weights=weights)

        x_starts = edges[:-1]
        x_ends = edges[1:]
        rect_data = np.stack((x_starts, x_ends, heights), axis=-1)

        plt.add_dataset(dict(
            source=rect_data,
            dimensions=['x_start', 'x_end', 'height']))

        plt.add_series(dict(
            name=str(col),
            type='custom',
            renderItem=MakeRectangles(),
            itemStyle=dict(opacity=opacity, color=palette[dataset_idx]),
            datasetIndex=dataset_idx,
            encode={
                'x': ['x_start', 'x_end'],
                'y': ['height']
            },
            clip=True
            ))
        plt.xAxis.type = 'value'
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
