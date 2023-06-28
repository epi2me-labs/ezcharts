"""Categorical plots."""

import numpy as np

from ezcharts.plots import Plot

__all__ = [
    "catplot", "stripplot", "swarmplot", "boxplot", "violinplot",
    "boxenplot", "pointplot", "barplot", "countplot"]


def catplot(*args, **kwargs):
    """Figure-level interface for drawing categorical plots in a grid."""
    raise NotImplementedError


def stripplot(*args, **kwargs):
    """Draw a scatterplot where one variable is categorical."""
    raise NotImplementedError


def swarmplot(*args, **kwargs):
    """Draw a categorical scatterplot with non-overlapping points."""
    raise NotImplementedError


def boxplot(*args, **kwargs):
    """Draw a box plot to show distributions with respect to categories."""
    raise NotImplementedError


def violinplot(*args, **kwargs):
    """Draw a combination of boxplot and kernel density estimate."""
    raise NotImplementedError


def boxenplot(*args, **kwargs):
    """Draw an enhanced box plot for larger datasets."""
    raise NotImplementedError


def pointplot(*args, **kwargs):
    """Show point estimates and confidence intervals using scatter plot."""
    # NOTE: default estimator is mean
    raise NotImplementedError


def barplot(
    data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
    estimator='mean', errorbar=('ci', 95), n_boot=1000, units=None, seed=None,
    orient=None, color=None, palette=None, saturation=0.75, width=0.8,
    errcolor='.26', errwidth=None, capsize=None, dodge=True, ci='deprecated',
        ax=None, **kwargs):
    """Show point estimates and confidence intervals as rectangular bars.

    Contrary to the seaborn implementation, setting `dodge=False` does not
    result in overlaying the bars, but rather stacking them.
    """
    x_name = x if x else data.columns[0]
    y_name = y if y else data.columns[1]

    plt = Plot()

    if hue not in data:
        data = data[[x_name, y_name]]
    else:
        # Transform to [x, hue, hue, hue ...]
        data = data.pivot(
            columns=hue, values=y_name, index=x_name).reset_index(drop=False)
        plt.legend = dict(orient='horizontal', top=25)

    if order:
        mapper = {x: pos for (pos, x) in enumerate(order)}
        data = data.sort_values(x_name, key=lambda x: x.map(mapper))

    plt.xAxis = dict(
        name=x_name,
        type='category',
        axisLabel=dict(interval=0, rotate=30),
        axisTick=dict(alignWithLabel=True))

    plt.yAxis = dict(name=y_name, type='value')

    plt.add_dataset({
        'id': 'raw',
        'dimensions': data.columns,
        'source': data.values})

    # If there are nan values, replace with zeros
    plt.dataset[0].source = np.nan_to_num(plt.dataset[0].source, nan=0)

    # Automatically map series to columns in the dataset
    if dodge:
        plt.series = [{'type': 'bar'}] * (data.shape[1] - 1)
    else:
        plt.series = [{'type': 'bar', 'stack': x_name}] * (data.shape[1] - 1)

    # Show a label per bar by default as ezcharts 'auto' method is very conservative.
    plt.xAxis.axisLabel = dict(interval=0)

    return plt


def countplot(*args, **kwargs):
    """Show the counts of observations in each categorical bin using bars."""
    raise NotImplementedError
