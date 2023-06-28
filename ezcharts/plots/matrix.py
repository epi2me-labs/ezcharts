"""Visualizing matrices of data."""
import pandas as pd
import seaborn as sns

from ezcharts.plots import Plot


__all__ = ["heatmap", "clustermap"]


def heatmap(
        data, *, vmin=None, vmax=None, cmap=None, center=None, robust=False,
        annot=True, fmt='.2g', annot_kws=None, linewidths=0, linecolor='white',
        cbar=True, cbar_kws=None, cbar_ax=None, square=False, xticklabels='auto',
        yticklabels='auto', mask=None, ax=None, **kwargs):
    """
    Plot rectangular data as a color-encoded matrix.

    Accepts a 2D dataset (list of lists) that can be coerced into an ndarray,
    or a Pandas dataframe.

    Data should be in a matrix where columns are the heatmap x axis and rows
    are the heatmap y axis.

    Axes titles are the name of the index or the columns. You can rename them
    like so:
    - index (x axis)
    data = data.rename_axis("x_axis_name")
    - columns (y axis)
    data = data.rename_axis("y_axis_name", axis=1)
    """
    # 2D arrays need to be reshaped using melt so they are the correct format
    # for add_dataset
    if not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    # Get data in format for ezcharts
    data = data.melt(ignore_index=False).reset_index().round(1)

    # If the user doesn't provide colors then default to something
    # that looks nice in our reports
    if cmap is None:
        cmap = sns.color_palette("viridis",  n_colors=1000, as_cmap=False).as_hex()

    # If the user doesn't provide minimum and maximums then work these
    # out from the data
    if vmin is None:
        vmin = data['value'].min()

    if vmax is None:
        vmax = data['value'].max()

    # Get the names for the axes
    x_name, y_name, plot_data = data.columns

    plt = Plot()

    plt.xAxis = dict(
        name=x_name,
        type='category',
        axisLabel=dict(
            interval=0,
            rotate=40
        ),
        axisTick=dict(
            alignWithLabel=True))

    plt.yAxis = dict(
        name=y_name,
        type='category',
        axisTick=dict(
            alignWithLabel=True))

    # On mouse over emphasize the heatmap tile
    emphasis_style = dict(
        itemStyle=dict(
            shadowBlur=10,
            shadowColor='#666666'))

    plt.series = [dict(
        type='heatmap',
        label=dict(show=annot),
        itemStyle=dict(borderWidth=linewidths, borderColor=linecolor),
        emphasis=emphasis_style)]

    plt.visualMap = [dict(
        min=vmin,
        max=vmax,
        calculable=True,
        left='right',
        top='center',
        orient='vertical',
        inRange=dict(color=cmap))]

    plt.add_dataset(dict(
        id='raw',
        dimensions=data.columns,
        source=data.values))

    return plt


def clustermap(*args, **kwargs):
    """Plot a matrix dataset as a hierarchically-clustered heatmap."""
    raise NotImplementedError
