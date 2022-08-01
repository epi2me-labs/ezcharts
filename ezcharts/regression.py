"""Regression plots."""

__all__ = ["lmplot", "regplot", "residplot"]


def lmplot(
        *, x=None, y=None, data=None, hue=None, col=None, row=None,
        palette=None, col_wrap=None, height=5, aspect=1, markers='o',
        sharex=None, sharey=None, hue_order=None, col_order=None,
        row_order=None, legend=True, legend_out=None, x_estimator=None,
        x_bins=None, x_ci='ci', scatter=True, fit_reg=True, ci=95, n_boot=1000,
        units=None, seed=None, order=1, logistic=False, lowess=False,
        robust=False, logx=False, x_partial=None, y_partial=None,
        truncate=True, x_jitter=None, y_jitter=None, scatter_kws=None,
        line_kws=None, facet_kws=None, size=None):
    """Plot data and regression model fits across a FacetGrid."""
    raise NotImplementedError


def regplot(
        *, x=None, y=None, data=None, x_estimator=None, x_bins=None,
        x_ci='ci', scatter=True, fit_reg=True, ci=95, n_boot=1000, units=None,
        seed=None, order=1, logistic=False, lowess=False, robust=False,
        logx=False, x_partial=None, y_partial=None, truncate=True, dropna=True,
        x_jitter=None, y_jitter=None, label=None, color=None, marker='o',
        scatter_kws=None, line_kws=None, ax=None):
    """Plot data and a linear regression model fit."""
    raise NotImplementedError


def residplot(
        *, x=None, y=None, data=None, lowess=False, x_partial=None,
        y_partial=None, order=1, robust=False, dropna=True, label=None,
        color=None, scatter_kws=None, line_kws=None, ax=None):
    """Plot the residuals of a linear regression."""
    raise NotImplementedError
