"""Relational plots."""

from seaborn.relational import _ScatterPlotter

from ezcharts.types import Plot


__all__ = ["relplot", "scatterplot", "lineplot"]


def relplot(
        *, x=None, y=None, hue=None, size=None, style=None, data=None,
        row=None, col=None, col_wrap=None, row_order=None, col_order=None,
        palette=None, hue_order=None, hue_norm=None, sizes=None,
        size_order=None, size_norm=None, markers=None, dashes=None,
        style_order=None, legend='auto', kind='scatter', height=5, aspect=1,
        facet_kws=None, units=None, **kwargs):
    """Figure-level interface for drawing relational plots onto a FacetGrid."""
    raise NotImplementedError


def scatterplot(
        *, x=None, y=None, hue=None, style=None, size=None, data=None,
        palette=None, hue_order=None, hue_norm=None, sizes=None,
        size_order=None, size_norm=None, markers=True, style_order=None,
        x_bins=None, y_bins=None, units=None, estimator=None, ci=95,
        n_boot=1000, alpha=None, x_jitter=None, y_jitter=None, legend='auto',
        ax=None, **kwargs):
    """Draw a scatter plot with possibility of several semantic groupings."""
    variables = _ScatterPlotter.get_semantics(locals())
    _p = _ScatterPlotter(data=data, variables=variables, legend=legend)
    data = _p.plot_data.dropna()
    if data.empty:
        return

    p = Plot()
    opt = p.opt
    opt.xAxis = dict(name=x)
    opt.yAxis = dict(name=y)
    opt.dataset = [{
        'id': 'raw',
        'dimensions': data.columns.tolist(),
        'source': data.values.tolist()}]
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

    return p


def lineplot(
        *, x=None, y=None, hue=None, size=None, style=None, data=None,
        palette=None, hue_order=None, hue_norm=None, sizes=None,
        size_order=None, size_norm=None, dashes=True, markers=None,
        style_order=None, units=None, estimator='mean', ci=95, n_boot=1000,
        seed=None, sort=True, err_style='band', err_kws=None, legend='auto',
        ax=None, **kwargs):
    """Draw a line plot with possibility of several semantic groupings."""
    raise NotImplementedError
