"""Categorical plots."""

__all__ = [
    "catplot", "stripplot", "swarmplot", "boxplot", "violinplot",
    "boxenplot", "pointplot", "barplot", "countplot"]


def catplot(
        *, x=None, y=None, hue=None, data=None, row=None, col=None,
        col_wrap=None, estimator=None, ci=95,
        n_boot=1000, units=None, seed=None, order=None, hue_order=None,
        row_order=None, col_order=None, kind='strip', height=5, aspect=1,
        orient=None, color=None, palette=None, legend=True, legend_out=True,
        sharex=True, sharey=True, margin_titles=False, facet_kws=None,
        **kwargs):
    """Figure-level interface for drawing categorical plots in a grid."""
    raise NotImplementedError


def stripplot(
        *, x=None, y=None, hue=None, data=None, order=None,
        hue_order=None, jitter=True, dodge=False, orient=None, color=None,
        palette=None, size=5, edgecolor='gray', linewidth=0, ax=None,
        **kwargs):
    """Draw a scatterplot where one variable is categorical."""
    raise NotImplementedError


def swarmplot(
        *, x=None, y=None, hue=None, data=None, order=None,
        hue_order=None, dodge=False, orient=None, color=None, palette=None,
        size=5, edgecolor='gray', linewidth=0, ax=None, **kwargs):
    """Draw a categorical scatterplot with non-overlapping points."""
    raise NotImplementedError


def boxplot(
        *, x=None, y=None, hue=None, data=None, order=None, hue_order=None,
        orient=None, color=None, palette=None, saturation=0.75, width=0.8,
        dodge=True, fliersize=5, linewidth=None, whis=1.5, ax=None, **kwargs):
    """Draw a box plot to show distributions with respect to categories."""
    raise NotImplementedError


def violinplot(
        *, x=None, y=None, hue=None, data=None, order=None,
        hue_order=None, bw='scott', cut=2, scale='area', scale_hue=True,
        gridsize=100, width=0.8, inner='box', split=False, dodge=True,
        orient=None, linewidth=None, color=None, palette=None, saturation=0.75,
        ax=None, **kwargs):
    """Draw a combination of boxplot and kernel density estimate."""
    raise NotImplementedError


def boxenplot(
        *, x=None, y=None, hue=None, data=None, order=None,
        hue_order=None, orient=None, color=None, palette=None, saturation=0.75,
        width=0.8, dodge=True, k_depth='tukey', linewidth=None,
        scale='exponential', outlier_prop=0.007, trust_alpha=0.05,
        showfliers=True, ax=None, **kwargs):
    """Draw an enhanced box plot for larger datasets."""
    raise NotImplementedError


def pointplot(
        *, x=None, y=None, hue=None, data=None, order=None,
        hue_order=None, estimator=None, ci=95,
        n_boot=1000, units=None, seed=None, markers='o', linestyles='-',
        dodge=False, join=True, scale=1, orient=None, color=None, palette=None,
        errwidth=None, capsize=None, ax=None, **kwargs):
    """Show point estimates and confidence intervals using scatter plot."""
    # NOTE: default estimator is mean
    raise NotImplementedError


def barplot(
        *, x=None, y=None, hue=None, data=None, order=None, hue_order=None,
        estimator=None, ci=95, n_boot=1000,
        units=None, seed=None, orient=None, color=None, palette=None,
        saturation=0.75, errcolor='.26', errwidth=None, capsize=None,
        dodge=True, ax=None, **kwargs):
    """Show point estimates and confidence intervals as rectangular bars."""
    # NOTE: default estimator is mean
    raise NotImplementedError


def countplot(
        *, x=None, y=None, hue=None, data=None, order=None,
        hue_order=None, orient=None, color=None, palette=None, saturation=0.75,
        dodge=True, ax=None, **kwargs):
    """Show the counts of observations in each categorical bin using bars."""
    raise NotImplementedError
