"""Relational plots."""

import numbers

from bokeh.models import HoverTool
from seaborn.relational import _LinePlotter, _ScatterPlotter

from ezcharts.plots import BokehPlot, util


__all__ = ["relplot", "scatterplot", "lineplot"]

DEFAULT_PALETTE = util.choose_palette()
DEFAULT_COLOR = DEFAULT_PALETTE[0]


def relplot(
        data=None, *,
        x=None, y=None, hue=None, size=None, style=None, units=None,
        row=None, col=None, col_wrap=None, row_order=None, col_order=None,
        palette=None, hue_order=None, hue_norm=None,
        sizes=None, size_order=None, size_norm=None,
        markers=None, dashes=None, style_order=None,
        legend="auto", kind="scatter", height=5, aspect=1, facet_kws=None,
        **kwargs):
    """Figure-level interface for drawing relational plots onto a FacetGrid."""
    raise NotImplementedError


class Mixin:
    """Mixin class to define how to plot lines and points."""

    def plot(self, plt: BokehPlot, kws):
        """Plot the plot."""
        # Get the potentially normalised data from seaborn
        data = self.plot_data.dropna()
        if data.empty:
            return

        if 'hue' not in data:
            # add a `hue` column (this can't be set to `None` as it would produce an
            # empty plot)
            data['hue'] = "values"

        x_name = self.variables.get("x", None)
        y_name = self.variables.get("y", None)

        symbol_size = kws.get('s', 8)
        if not isinstance(symbol_size, numbers.Number):
            raise NotImplementedError(
                "symbol size (s) currently only accepts a constant value")

        line_width = kws.get('linewidth', 3)
        if not isinstance(line_width, numbers.Number):
            raise NotImplementedError(
                "linewidth currently only accepts a constant value")

        # Available markers/glyphs can be found here:
        # https://docs.bokeh.org/en/latest/docs/reference/models/glyphs.html
        marker = kws.get('marker')
        # TODO: size and style are also grouping "semantic" variables

        y_min = 0
        for hue_name, df in data.groupby('hue'):
            relational_kwargs = {}
            if data['hue'].nunique() > 1:
                relational_kwargs["legend_label"] = hue_name

            y_min = min(y_min, df.y.min())
            color = kws.get("color")
            if self._hue_map.levels:
                # the hue map is not empty (i.e. it was initialised with a palette); use
                # this to override the color (in case one was passed)
                color = self._hue_map(hue_name)

            if self.series_type == 'line':
                plt._fig.line(
                    df.x, df.y, line_color=color,
                    line_width=line_width, **relational_kwargs)

            elif self.series_type == 'scatter':
                plt._fig.scatter(
                    df.x, df.y, color=color, **relational_kwargs)

            if marker is not False:
                if marker is None or marker is True:
                    marker = 'circle'
                # Use scatter to add the markers
                plt._fig.scatter(
                    df.x, df.y, size=symbol_size, marker=marker,
                    color=color, **relational_kwargs)

            plt._fig.xaxis.axis_label = x_name
            plt._fig.yaxis.axis_label = y_name

        # Default the y_range start to zero unless y contains negative values.
        plt._fig.y_range.start = y_min

        # TODO: add legend
        return plt


class ScatterPlotter(Mixin, _ScatterPlotter):
    """Making scatter plots."""

    series_type = 'scatter'


def scatterplot(
        data=None, *,
        x=None, y=None, hue=None, size=None, style=None,
        palette=None, hue_order=None, hue_norm=None,
        sizes=None, size_order=None, size_norm=None,
        markers=True, style_order=None, legend="auto", ax=None,
        bokeh_kwargs={}, **kwargs):
    """Draw a scatter plot with possibility of several semantic groupings."""
    # see https://github.com/mwaskom/seaborn/blob/949dec3666ab12a366d2fc05ef18d6e90625b5fa/seaborn/relational.py#L726  # noqa

    if palette is None:
        palette = DEFAULT_PALETTE

    if not kwargs.get("color"):
        kwargs["color"] = DEFAULT_COLOR

    # TODO: what of this do we actually care for
    variables = ScatterPlotter.get_semantics(locals())
    p = ScatterPlotter(data=data, variables=variables, legend=legend)
    p.map_hue(palette=palette, order=hue_order, norm=hue_norm)
    p.map_size(sizes=sizes, order=size_order, norm=size_norm)
    p.map_style(markers=markers, order=style_order)

    plt = BokehPlot(title=kwargs.get('title', ""), **bokeh_kwargs)
    hover = plt._fig.select(dict(type=HoverTool))
    hover.tooltips = [(x, "@x"), (y, "@y")]
    p.plot(plt, kwargs)

    return plt


class LinePlotter(Mixin, _LinePlotter):
    """Making line plots."""

    series_type = 'line'


def lineplot(
        data=None, *,
        x=None, y=None, hue=None, size=None, style=None, units=None,
        palette=None, hue_order=None, hue_norm=None,
        sizes=None, size_order=None, size_norm=None,
        dashes=True, markers=None, style_order=None,
        estimator="mean", errorbar=("ci", 95), n_boot=1000, seed=None,
        orient="x", sort=True, err_style="band", err_kws=None,
        legend="auto", ci="deprecated", ax=None, bokeh_kwargs={}, **kwargs):
    """Draw a line plot with possibility of several semantic groupings."""
    # see https://github.com/mwaskom/seaborn/blob/949dec3666ab12a366d2fc05ef18d6e90625b5fa/seaborn/relational.py#L597  # noqa

    if palette is None:
        palette = DEFAULT_PALETTE

    if not kwargs.get("color"):
        kwargs["color"] = DEFAULT_COLOR

    # TODO: what of this do we actually care for
    variables = _LinePlotter.get_semantics(locals())
    p = LinePlotter(
        data=data, variables=variables, estimator=estimator, n_boot=n_boot,
        seed=seed, errorbar=errorbar, sort=sort, orient=orient,
        err_style=err_style, err_kws=err_kws, legend=legend)
    p.map_hue(palette=palette, order=hue_order, norm=hue_norm)
    p.map_size(sizes=sizes, order=size_order, norm=size_norm)
    p.map_style(markers=markers, dashes=dashes, order=style_order)

    plt = BokehPlot(title=kwargs.get('title', ""), **bokeh_kwargs)
    hover = plt._fig.select(dict(type=HoverTool))
    hover.tooltips = [(x, "@x"), (y, "@y")]

    p.plot(plt, kwargs)
    return plt
