"""Relational plots."""

from seaborn.relational import _LinePlotter, _ScatterPlotter

from ezcharts.plots import util
from ezcharts.plots.types import Plot


__all__ = ["relplot", "scatterplot", "lineplot"]


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


class ScatterPlotter(_ScatterPlotter):
    """Making scatter plots."""

    def plot(self, plt, kws):
        """Plot the plot."""
        data = self.plot_data.dropna()
        if data.empty:
            return

        opt = plt.opt
        opt.xAxis = {
            "name": self.variables.get("x", None),
            "type": util.sns_type_to_echarts[str(self.var_types['x'])]}
        opt.yAxis = dict(
            name=self.variables.get("y", None),
            type=util.sns_type_to_echarts[str(self.var_types['y'])])
        opt.dataset = [{
            'id': 'raw',
            'dimensions': data.columns.tolist(),
            'source': data.values.tolist()}]
        # TODO: size and style are also grouping "semantic" variables
        for series_name in data['hue'].unique():
            opt.dataset.append({
                'id': series_name,
                'fromDatasetId': 'raw',
                'transform': {
                    'type': 'filter',
                    'config': {'dimension': 'hue', '=': series_name}}})
            opt.add_series({
                'type': 'scatter',
                'datasetId': series_name,
                'encode': {'x': 'x', 'y': 'y'}})

        # TODO: add legend
        return


def scatterplot(
        data=None, *,
        x=None, y=None, hue=None, size=None, style=None,
        palette=None, hue_order=None, hue_norm=None,
        sizes=None, size_order=None, size_norm=None,
        markers=True, style_order=None, legend="auto", ax=None,
        **kwargs):
    """Draw a scatter plot with possibility of several semantic groupings."""
    # see https://github.com/mwaskom/seaborn/blob/949dec3666ab12a366d2fc05ef18d6e90625b5fa/seaborn/relational.py#L726  # noqa

    # TODO: what of this do we actually care for
    variables = ScatterPlotter.get_semantics(locals())
    p = ScatterPlotter(data=data, variables=variables, legend=legend)
    p.map_hue(palette=palette, order=hue_order, norm=hue_norm)
    p.map_size(sizes=sizes, order=size_order, norm=size_norm)
    p.map_style(markers=markers, order=style_order)

    plt = Plot()
    p.plot(plt, kwargs)
    return plt


class LinePlotter(_LinePlotter):
    """Making line plots."""

    def plot(self, plt, kws):
        """Plot the plot."""
        # TODO: handle all the fancy stuff

        data = self.plot_data.dropna()
        if data.empty:
            return

        opt = plt.opt
        opt.xAxis = dict(
            name=self.variables.get("x", None),
            type=util.sns_type_to_echarts[str(self.var_types['x'])])
        opt.yAxis = dict(
            name=self.variables.get("y", None),
            type=util.sns_type_to_echarts[str(self.var_types['y'])])
        opt.dataset = [{
            'id': 'raw',
            'dimensions': data.columns.tolist(),
            'source': data.values.tolist()}]
        opt.dataset = [{
            'id': 'raw',
            'dimensions': data.columns.tolist(),
            'source': data.values.tolist()}]
        # TODO: size and style are also grouping "semantic" variables
        for series_name in data['hue'].unique():
            opt.dataset.append({
                'id': series_name,
                'fromDatasetId': 'raw',
                'transform': {
                    'type': 'filter',
                    'config': {'dimension': 'hue', '=': series_name}}})
            opt.add_series({
                'type': 'line',
                'datasetId': series_name,
                'encode': {'x': 'x', 'y': 'y'}})

        # TODO: add legend
        return


def lineplot(
        data=None, *,
        x=None, y=None, hue=None, size=None, style=None, units=None,
        palette=None, hue_order=None, hue_norm=None,
        sizes=None, size_order=None, size_norm=None,
        dashes=True, markers=None, style_order=None,
        estimator="mean", errorbar=("ci", 95), n_boot=1000, seed=None,
        orient="x", sort=True, err_style="band", err_kws=None,
        legend="auto", ci="deprecated", ax=None, **kwargs):
    """Draw a line plot with possibility of several semantic groupings."""
    # see https://github.com/mwaskom/seaborn/blob/949dec3666ab12a366d2fc05ef18d6e90625b5fa/seaborn/relational.py#L597  # noqa

    # TODO: what of this do we actually care for
    variables = _LinePlotter.get_semantics(locals())
    p = LinePlotter(
        data=data, variables=variables, estimator=estimator, n_boot=n_boot,
        seed=seed, errorbar=errorbar, sort=sort, orient=orient,
        err_style=err_style, err_kws=err_kws, legend=legend)
    p.map_hue(palette=palette, order=hue_order, norm=hue_norm)
    p.map_size(sizes=sizes, order=size_order, norm=size_norm)
    p.map_style(markers=markers, dashes=dashes, order=style_order)

    plt = Plot()
    p.plot(plt, kwargs)
    return plt