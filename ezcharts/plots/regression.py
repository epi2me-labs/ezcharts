"""Regression plots."""

__all__ = ["lmplot", "regplot", "residplot"]


def lmplot(*args, **kwargs):
    """Plot data and regression model fits across a FacetGrid."""
    raise NotImplementedError


def regplot(*args, **kwargs):
    """Plot data and a linear regression model fit."""
    raise NotImplementedError


def residplot(*args, **kwargs):
    """Plot the residuals of a linear regression."""
    raise NotImplementedError
