"""Categorical plots."""

from bokeh.models import ColumnDataSource
import bokeh.transform as bkt
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
    ax=None, **kwargs,
):
    """Show point estimates as rectangular bars.

    Contrary to the seaborn implementation, setting `dodge=False` does not
    result in overlaying the bars, but rather stacking them.
    """
    # use our default palette if no colour options were provided
    if palette is None and color is None:
        palette = BokehPlot.colors

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

    plotter.group_names = [str(x) for x in plotter.group_names]

    if plotter.orient == "v":
        plt = BokehPlot(x_range=plotter.group_names)
    else:
        plt = BokehPlot(y_range=plotter.group_names)

    p = plt._fig

    if plotter.plot_hues is None:
        # simple barplot (i.e. only a single group of bars)
        if plotter.orient == "v":
            p.vbar(
                x=plotter.group_names,
                top=plotter.statistic,
                width=0.9,
                color=plotter.colors.as_hex(),
                **kwargs,
            )
        else:
            p.hbar(
                y=plotter.group_names,
                right=plotter.statistic,
                height=0.9,
                color=plotter.colors.as_hex(),
                **kwargs,
            )
    else:
        # groups of bars (either stacked or grouped)
        data = dict(groups=plotter.group_names)
        data.update(dict(zip(plotter.hue_names, plotter.statistic.T)))
        data = ColumnDataSource(data)

        if not dodge:
            if plotter.orient == "v":
                # stacked vertical bars
                p.vbar_stack(
                    plotter.hue_names,
                    x="groups",
                    width=0.95,
                    color=plotter.colors.as_hex(),
                    source=data,
                    legend_label=plotter.hue_names,
                    **kwargs
                )
            else:
                # stacked horizontal bars
                p.hbar_stack(
                    plotter.hue_names,
                    y="groups",
                    height=0.95,
                    color=plotter.colors.as_hex(),
                    source=data,
                    legend_label=plotter.hue_names,
                    **kwargs
                )
        else:
            # grouped plots (we need to add a series for each hue level)
            for hue_level, offset, color in zip(
                plotter.hue_names,
                plotter.hue_offsets,
                plotter.colors.as_hex(),
            ):
                plot_bars_kwargs = dict(
                    source=data,
                    color=color,
                    line_color="white",
                    legend_label=hue_level,
                )
                if plotter.orient == "v":
                    plot_bars_func = p.vbar
                    plot_bars_kwargs.update(
                        dict(
                            x=bkt.dodge("groups", offset, range=p.x_range),
                            top=hue_level,
                            width=plotter.nested_width,
                        )
                    )
                else:
                    plot_bars_func = p.hbar
                    plot_bars_kwargs.update(
                        dict(
                            y=bkt.dodge("groups", offset, range=p.y_range),
                            right=hue_level,
                            height=plotter.nested_width,
                        )
                    )
                plot_bars_func(**plot_bars_kwargs, **kwargs)

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
