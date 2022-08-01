"""Distributional plots."""

__all__ = ["displot", "histplot", "kdeplot", "ecdfplot", "rugplot", "distplot"]


def displot(
        data=None, *, x=None, y=None, hue=None, row=None, col=None,
        weights=None, kind='hist', rug=False, rug_kws=None, log_scale=None,
        legend=True, palette=None, hue_order=None, hue_norm=None, color=None,
        col_wrap=None, row_order=None, col_order=None, height=5, aspect=1,
        facet_kws=None, **kwargs):
    """Figure-level interface for distribution plots in a grid."""
    raise NotImplementedError


def histplot(
        data=None, *, x=None, y=None, hue=None, weights=None,
        stat='count', bins='auto', binwidth=None, binrange=None, discrete=None,
        cumulative=False, common_bins=True, common_norm=True, multiple='layer',
        element='bars', fill=True, shrink=1, kde=False, kde_kws=None,
        line_kws=None, thresh=0, pthresh=None, pmax=None, cbar=False,
        cbar_ax=None, cbar_kws=None, palette=None, hue_order=None,
        hue_norm=None, color=None, log_scale=None, legend=True, ax=None,
        **kwargs):
    """Plot univariate or bivariate histograms to show distributions."""
    raise NotImplementedError


def kdeplot(
        x=None, *, y=None, shade=None, vertical=False, kernel=None,
        bw=None, gridsize=200, cut=3, clip=None, legend=True, cumulative=False,
        shade_lowest=None, cbar=False, cbar_ax=None, cbar_kws=None, ax=None,
        weights=None, hue=None, palette=None, hue_order=None, hue_norm=None,
        multiple='layer', common_norm=True, common_grid=False, levels=10,
        thresh=0.05, bw_method='scott', bw_adjust=1, log_scale=None,
        color=None, fill=None, data=None, data2=None, warn_singular=True,
        **kwargs):
    """Plot uni/bi-variate distributions using kernel density estimation."""
    raise NotImplementedError


def ecdfplot(
        data=None, *, x=None, y=None, hue=None, weights=None,
        stat='proportion', complementary=False, palette=None, hue_order=None,
        hue_norm=None, log_scale=None, legend=True, ax=None, **kwargs):
    """Plot empirical cumulative distribution functions."""
    raise NotImplementedError


def rugplot(
        x=None, *, height=0.025, axis=None, ax=None, data=None, y=None,
        hue=None, palette=None, hue_order=None, hue_norm=None,
        expand_margins=True, legend=True, a=None, **kwargs):
    """Plot marginal distributions by drawing ticks along the x and y axes."""
    raise NotImplementedError


def distplot(
        a=None, bins=None, hist=True, kde=True, rug=False, fit=None,
        hist_kws=None, kde_kws=None, rug_kws=None, fit_kws=None, color=None,
        vertical=False, norm_hist=False, axlabel=None, label=None, ax=None,
        x=None):
    """Flexibly plot a univariate distribution of observations (DEPRECATED)."""
    raise DeprecationWarning
    raise NotImplementedError
