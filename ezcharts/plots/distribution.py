"""Distributional plots."""

__all__ = ["displot", "histplot", "kdeplot", "ecdfplot", "rugplot", "distplot"]


def displot(*args, **kwargs):
    """Figure-level interface for distribution plots in a grid."""
    raise NotImplementedError


def histplot(*args, **kwargs):
    """Plot univariate or bivariate histograms to show distributions."""
    raise NotImplementedError


def kdeplot(*args, **kwargs):
    """Plot uni/bi-variate distributions using kernel density estimation."""
    raise NotImplementedError


def ecdfplot(*args, **kwargs):
    """Plot empirical cumulative distribution functions."""
    raise NotImplementedError


def rugplot(*args, **kwargs):
    """Plot marginal distributions by drawing ticks along the x and y axes."""
    raise NotImplementedError


def distplot(*args, **kwargs):
    """Flexibly plot a univariate distribution of observations (DEPRECATED)."""
    raise DeprecationWarning
    raise NotImplementedError
