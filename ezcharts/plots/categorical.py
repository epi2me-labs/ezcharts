"""Categorical plots."""
from collections import Counter
from itertools import cycle

from bokeh.models import ColumnDataSource, FactorRange, HoverTool, Whisker
import bokeh.transform as bkt
import numpy as np
import pandas as pd
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


def boxplot(
        data=None, *, x=None, y=None, hue=None, order=None, hue_order=None,
        orient=None, color=None, palette=None, saturation=1, fill=True,
        dodge=None, width=None, gap=None, whis=1.5, linecolor='auto', linewidth=1,
        fliersize=6, hue_norm=None, native_scale=None, log_scale=None,
        formatter=None, legend=None, ax=None, **kwargs):
    """Draw a box plot to show distributions with respect to categories."""
    # deal with stuff we haven't implemented, yet
    not_implemented = [
        hue, hue_order, orient, dodge, width, ax, formatter, legend,
        gap, hue_norm, native_scale, log_scale]
    for i in not_implemented:
        if i is not None:
            raise NotImplementedError(
                f"The parameter with the value {i} is not yet implemented.")

    # use our default palette if no colour options were provided
    if palette is None and color is None:
        palette = BokehPlot.colors

    # If data is list-like make it into a dataframe
    if not isinstance(data, pd.DataFrame):
        if x is None:
            x = "variable"
        if y is None:
            y = "value"
        # Use dummy column x for grouping variable
        data = pd.DataFrame({x: "0", y: data})

    if x is None:
        x = data.columns[0]
    if y is None:
        y = data.columns[1]

    # we are going to group by our x
    groups = data[x].unique()

    # compute quantiles
    qs = data.groupby(x)[y].quantile([0.25, 0.5, 0.75])
    qs = qs.unstack().reset_index()
    qs.columns = [x, "q1", "q2", "q3"]
    df = pd.merge(data, qs, on=x, how="left")

    # compute mean, min and max for hover
    mean_val = df.groupby(x)[y].mean().reset_index()
    mean_val.columns = [x, "mean"]
    df = pd.merge(df, mean_val, on=x, how="left")
    min_val = df.groupby(x)[y].min().reset_index()
    min_val.columns = [x, "min"]
    df = pd.merge(df, min_val, on=x, how="left")
    max_val = df.groupby(x)[y].max().reset_index()
    max_val.columns = [x, "max"]
    df = pd.merge(df, max_val, on=x, how="left")

    # if the user specifies an order for their categorical variables
    if isinstance(order, list):
        # check to make sure user has included all categorical variables
        check = Counter(order) == Counter(groups)
        if check:
            groups = order
        else:
            raise ValueError(
                f"all categories ({groups}) not present in order ({order})")

    # compute IQR outlier bounds
    iqr = df.q3 - df.q1

    # whiskers
    if isinstance(whis, float):
        df["upper"] = df.q3 + whis * iqr
        df["lower"] = df.q1 - whis * iqr
    else:
        raise NotImplementedError(
            f"'whis' must be float, {type(whis)} is not supported or implemented")

    # Use only grouped stats to make the plot
    plot_df = df.drop(y, axis=1).drop_duplicates()
    source = ColumnDataSource(plot_df)

    # quantile boxes color
    if not color:
        if len(palette) < len(groups):
            # cycle palette to add more colours
            for c, _ in zip(cycle(palette), range(len(palette), len(groups))):
                palette.append(c)
        color = bkt.factor_cmap(x, palette, groups)

    # use seaborn bits and bobs for color
    if not fill:
        color = None
        linecolor = "black"
    else:
        if linecolor == 'auto':
            linecolor = "black"

    # outlier range
    whisker = Whisker(
        base=x, upper="upper", lower="lower", source=source,
        line_width=linewidth, line_color=linecolor)

    whisker.upper_head.size = whisker.lower_head.size = 20

    # outliers
    outliers = df[~df[y].between(df.lower, df.upper)]

    # we need to accpount for whskers and outliers in the y-range
    y_min = df["lower"].min()
    y_max = df["upper"].max()

    # if there are outliers then we need to take those into account
    if not outliers.empty:
        y_min = np.min([outliers[y].min(), df["lower"].min()])
        y_max = np.max([outliers[y].max(), df["upper"].max()])

    y_range = (1.1 * y_min, 1.1 * y_max)

    plt = BokehPlot(x_range=groups, y_range=y_range)
    p = plt._fig
    p.add_layout(whisker)

    p.vbar(
        x, 0.7, "q2", "q3", source=source, fill_color=color, line_color=linecolor,
        line_width=linewidth, fill_alpha=saturation)

    p.vbar(
        x, 0.7, "q1", "q2", source=source, fill_color=color, line_color=linecolor,
        line_width=linewidth, fill_alpha=saturation)

    p.scatter(x, y, source=outliers, size=fliersize, color="black", alpha=0.5)

    p.xgrid.grid_line_color = None
    p.xaxis.axis_label = x.capitalize()
    p.yaxis.axis_label = y.capitalize()

    # Add tooltips
    hover = plt._fig.select(dict(type=HoverTool))
    hover.tooltips = [
        ("Q1", "@q1"),
        ("Median", "@q2"),
        ("Q3", "@q3"),
        ("Mean", "@mean"),
        ("Min", "@min"),
        ("Max", "@max")
    ]

    return plt


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

    if not nested_x:
        p.xaxis.axis_label = x.capitalize()
        p.yaxis.axis_label = y.capitalize()

    plt_df = plt._fig.renderers[0].data_source.to_df()
    hover = plt._fig.select(dict(type=HoverTool))
    if 'top' in plt_df.columns:
        hover.tooltips = [(y, "@top")]
    elif not nested_x:
        hover.tooltips = [
            (colname, '@{' + colname + '}')
            for colname in plt_df.columns
            if colname != 'groups'
        ]
    else:
        hover.tooltips = [
            (y, '@y')
        ]
    return plt


def countplot(*args, **kwargs):
    """Show the counts of observations in each categorical bin using bars."""
    raise NotImplementedError
