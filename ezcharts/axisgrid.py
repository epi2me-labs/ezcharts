"""Mulit-plot grids."""

__all__ = ['pairplot', 'jointplot']


def pairplot(
        data, *, hue=None, hue_order=None, palette=None, vars=None,
        x_vars=None, y_vars=None, kind='scatter', diag_kind='auto',
        markers=None, height=2.5, aspect=1, corner=False, dropna=False,
        plot_kws=None, diag_kws=None, grid_kws=None, size=None):
    """Plot pairwise relationships in a dataset."""
    raise NotImplementedError


def jointplot(
        *, x=None, y=None, data=None, kind='scatter', color=None,
        height=6, ratio=5, space=0.2, dropna=False, xlim=None, ylim=None,
        marginal_ticks=False, joint_kws=None, marginal_kws=None, hue=None,
        palette=None, hue_order=None, hue_norm=None, **kwargs):
    """Draw a plot of two variables with bivariate and univariate graphs."""
    raise NotImplementedError
