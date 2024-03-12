"""Categorical plots."""

from bokeh.models import ColumnDataSource, FactorRange
import bokeh.transform as bkt
import numpy as np
from seaborn.categorical import _BarPlotter

from ezcharts.plots import BokehPlot


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
    orient=None, color=None, palette=None, saturation=1.0, width=0.8,
    errcolor='.26', errwidth=None, capsize=None, dodge=True, ci='deprecated',
    ax=None, nested_x=False, **kwargs,
):
    """Show point estimates as rectangular bars.

    Contrary to the seaborn implementation, setting `dodge=False` does not
    result in overlaying the bars, but rather stacking them.

    nested_x: create a nested plot instead of a grouped plot, which has two X
    axis grouping (hue as outer group)
    """
    # use our default palette if no colour options were provided
    if palette is None and color is None:
        palette = BokehPlot.colors

    # A plot can either be nested or stacked, not both
    if nested_x:
        if hue is None or not dodge:
            raise ValueError(
                "`hue` and `dodge` need to be set when passing `nested_x=True`"
            )
        if orient == "h":
            raise ValueError(
                "`nested_x=True` can only work with `orient='v'`"
            )

    # Create bar plot with seaborn
    plotter = _BarPlotter(
        x,
        y,
        hue,
        data,
        order,
        hue_order,
        estimator,
        errorbar,
        n_boot,
        units,
        seed,
        orient,
        color,
        palette,
        saturation,
        width,
        errcolor,
        errwidth,
        capsize,
        dodge,
    )

    # Nested X labeling requires the factors to be provided as a list of
    # tuples with the hue and x levels for each value in the dataframe:
    # factors = [
    #   ("hue1", "x1"),
    #   ("hue1", "x2"),
    #   ("hue2", "x1"),
    #   ("hue2", "x2"),
    # ]
    if nested_x:
        factors = [
            (str(x0), str(x1)) for x0 in plotter.hue_names for x1 in plotter.group_names
        ]
        group_names = FactorRange(*factors)
    else:
        group_names = [str(x) for x in plotter.group_names]

    if plotter.orient == "v":
        plt = BokehPlot(x_range=group_names)
    else:
        plt = BokehPlot(y_range=group_names)

    p = plt._fig

    # Define plot orientation
    # If both hue and dodge=False are provided, make a stacked bar chart
    if plotter.orient == "v":
        plot_bars_func = p.vbar_stack if not dodge and hue else p.vbar
    else:
        plot_bars_func = p.hbar_stack if not dodge and hue else p.hbar

    if plotter.plot_hues is None:
        # simple barplot (i.e. only a single group of bars)
        if plotter.orient == "v":
            plot_bars_func(
                x=group_names,
                top=plotter.statistic,
                width=0.9,
                color=plotter.colors.as_hex(),
                **kwargs
            )
        else:
            plot_bars_func(
                y=group_names,
                right=plotter.statistic,
                height=0.9,
                color=plotter.colors.as_hex(),
                **kwargs
            )
    elif nested_x:
        # Nested X uses different labelling of the input values
        # x: list of factors described above
        # y: values in a single list/vector
        # legend_name: point to to the legend labelling
        # Create the legend labels
        dual_legend_label = [
            str(x0) for x0 in plotter.hue_names for _ in plotter.group_names
        ]
        # Create the data structure
        data = dict(
            x=factors, y=np.hstack(plotter.statistic.T), legend_name=dual_legend_label
        )
        # Convert to ColumnDataSource
        data = ColumnDataSource(data)
        plot_bars_func(
            x="x",
            top="y",
            source=data,
            line_color="white",
            legend_field="legend_name",
            color=bkt.factor_cmap(
                "x", palette=plotter.colors.as_hex(), factors=plotter.hue_names, end=1
            ),
            **kwargs,
        )
    else:
        data = dict(groups=plotter.group_names)
        data.update(dict(zip(plotter.hue_names, plotter.statistic.T)))
        data = ColumnDataSource(data)
        if not dodge:
            # stacked bars (define orientation-specific kwargs first)
            if plotter.orient == "v":
                extra_kwargs = dict(x="groups", width=0.95)
            else:
                extra_kwargs = dict(y="groups", height=0.95)
            plot_bars_func(
                plotter.hue_names,
                color=plotter.colors.as_hex(),
                source=data,
                legend_label=plotter.hue_names,
                **extra_kwargs,
                **kwargs,
            )
        else:
            # grouped bars (we need to add a series for each hue level)
            for hue_level, offset, color in zip(
                plotter.hue_names,
                plotter.hue_offsets,
                plotter.colors.as_hex(),
            ):
                # define orientation-specific kwargs
                if plotter.orient == "v":
                    extra_kwargs = dict(
                        x=bkt.dodge("groups", offset, range=p.x_range),
                        top=hue_level,
                        width=plotter.nested_width,
                    )
                else:
                    extra_kwargs = dict(
                        y=bkt.dodge("groups", offset, range=p.y_range),
                        right=hue_level,
                        height=plotter.nested_width,
                    )
                plot_bars_func(
                    source=data,
                    color=color,
                    line_color="white",
                    legend_label=hue_level,
                    **extra_kwargs,
                    **kwargs,
                )

        p.legend.orientation = "horizontal"
        # even though we call `add_layout()` to pull the legend outside of the plot area
        # below, we still need to set `location` to "top" here to make sure the legend
        # is centered properly
        p.legend.location = "top"
        p.add_layout(p.legend[0], "above")

    if plotter.orient == "v":
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
    else:
        p.ygrid.grid_line_color = None
        p.x_range.start = 0

    return plt


def countplot(*args, **kwargs):
    """Show the counts of observations in each categorical bin using bars."""
    raise NotImplementedError
