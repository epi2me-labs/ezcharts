"""Visualizing matrices of data."""

__all__ = ["heatmap", "clustermap"]


def heatmap(
        data, *, vmin=None, vmax=None, cmap=None, center=None,
        robust=False, annot=None, fmt='.2g', annot_kws=None, linewidths=0,
        linecolor='white', cbar=True, cbar_kws=None, cbar_ax=None,
        square=False, xticklabels='auto', yticklabels='auto', mask=None,
        ax=None, **kwargs):
    """Plot rectangular data as a color-encoded matrix."""
    raise NotImplementedError


def clustermap(
        data, *, pivot_kws=None, method='average', metric='euclidean',
        z_score=None, standard_scale=None, figsize=(
        10, 10), cbar_kws=None,
        row_cluster=True, col_cluster=True, row_linkage=None, col_linkage=None,
        row_colors=None, col_colors=None, mask=None, dendrogram_ratio=0.2,
        colors_ratio=0.03, cbar_pos=(
        0.02, 0.8, 0.05, 0.18), tree_kws=None,
        **kwargs):
    """Plot a matrix dataset as a hierarchically-clustered heatmap."""
    raise NotImplementedError
