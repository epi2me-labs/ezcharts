"""Categorical plots."""

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


def barplot(*args, **kwargs):
    """Show point estimates and confidence intervals as rectangular bars."""
    # NOTE: default estimator is mean
    raise NotImplementedError


def countplot(*args, **kwargs):
    """Show the counts of observations in each categorical bin using bars."""
    raise NotImplementedError
