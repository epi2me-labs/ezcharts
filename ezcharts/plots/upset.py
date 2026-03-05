"""UpSet plot for visualising set intersections."""

from bokeh.layouts import gridplot
from bokeh.models import (
    ColumnDataSource,
    CustomJSTickFormatter,
    HoverTool,
    Range1d,
)
from bokeh.plotting import figure
import pandas as pd

from ezcharts.plots import BokehPlot

__all__ = ["UpSetPlot"]


class UpSetPlot(BokehPlot):
    """
    Multi-panel UpSet plot for visualising set intersections.

    Creates a linked view of:
    - Intersection size bar chart (top)
    - Dot matrix showing set membership per intersection (bottom right)
    - Per-set totals horizontal bar chart (bottom left, optional)

    Example input DataFrame::

        df = pd.DataFrame({
            "set_A": [True,  True,  True,  False, False, False],
            "set_B": [False, True,  True,  True,  True,  False],
            "set_C": [False, False, True,  False, True,  True],
            "size":  [45,    23,    8,     30,    12,    20],
        })
        plt = UpSetPlot(df, sets=["set_A", "set_B", "set_C"])

    """

    def __init__(
        self,
        data,
        sets,
        size_col="size",
        sort_by="cardinality",
        min_subset_size=None,
        max_subsets=None,
        bar_color="#007FA9",
        dot_color=None,
        inactive_dot_color="#d3d3d3",
        show_totals=True,
        title="",
        bar_ylabel="Number of reads",
        totals_xlabel="Number of reads",
        height_bars=250,
        height_matrix=120,
        width_matrix=600,
        width_totals=200,
    ):
        """
        Initialise UpSet plot.

        Parameters
        ----------
        data : pd.DataFrame
            One row per intersection. Must contain:
            - One boolean column per set, where True indicates that set
            is a member of the intersection in that row
            - A numeric column containing the size of each intersection
        sets : list of str
            Names of the boolean columns in `data` that represent set
            membership
        size_col : str, default "size"
            Column name containing intersection sizes.
        sort_by : str or None, default "cardinality"
            How to order intersections. "cardinality" sorts by size descending,
            "degree" sorts by number of sets in the intersection, None preserves
            input order.
        min_subset_size : int, optional
            Exclude intersections smaller than this value.
        max_subsets : int, optional
            Maximum number of intersections to display. Applied after sorting,
            so with sort_by="cardinality" the largest intersections are kept.
            If sort_by=None, the first n intersections are kept.
        bar_color : str, default "#007FA9"
            Colour for intersection size bars and active dots.
        dot_color : str, optional
            Override colour for active dots specifically. Falls back to
            bar_color if not provided.
        inactive_dot_color : str, default "#d3d3d3"
            Colour for dots representing sets absent from an intersection.
        show_totals : bool, default True
            Whether to show the per-set totals panel on the left.
        title : str, default ""
            Optional title shown above the intersection bar chart.
        bar_ylabel : str, default "Number of reads"
            Y-axis label for the intersection size bar chart.
        totals_xlabel : str, default "Number of reads"
            X-axis label for the per-set totals bar chart.
        height_bars : int, default 250
            Height in pixels of the intersection size bar chart.
        height_matrix : int, default 120
            Height in pixels of the dot matrix (and totals) panel.
        width_matrix : int, default 600
            Width in pixels of the dot matrix panel.
        width_totals : int, default 200
            Width in pixels of the set totals panel.
        """
        self.sets = sets
        self.size_col = size_col
        self.sort_by = sort_by
        self.min_subset_size = min_subset_size
        self.max_subsets = max_subsets
        self.bar_color = bar_color
        self.dot_color = dot_color or bar_color
        self.inactive_dot_color = inactive_dot_color
        self.show_totals = show_totals
        self.title = title
        self.bar_ylabel = bar_ylabel
        self.totals_xlabel = totals_xlabel
        self.height_bars = height_bars
        self.height_matrix = height_matrix
        self.width_matrix = width_matrix
        self.width_totals = width_totals

        self._validate_data(data)
        self.data = self._prepare_data(data)

        # Categorical x-axis positions matching DataFrame index
        self.x_coords = [str(i) for i in self.data.index]

        self._build_plots()

        super().__init__()
        self._fig = self._compose_grid()

    def _validate_data(self, data):
        """Validate input DataFrame has required columns and correct types."""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")

        if len(self.sets) == 0:
            raise ValueError("At least one set must be provided in `sets`.")

        missing = [c for c in self.sets + [self.size_col] if c not in data.columns]
        if missing:
            raise ValueError(f"Columns not found in data: {missing}")

        if self.sort_by not in ("cardinality", "degree", None):
            raise ValueError("sort_by must be 'cardinality', 'degree', or None")

        if self.max_subsets is not None and self.max_subsets < 1:
            raise ValueError("max_subsets must be a positive integer or None.")

    def _prepare_data(self, data):
        """Filter and sort the intersection DataFrame."""
        df = data.copy()

        # Filter data
        if self.min_subset_size is not None:
            df = df[df[self.size_col] >= self.min_subset_size]
        if df.empty:
            raise ValueError(
                "No intersections remain after filtering. "
                "Check min_subset_size."
            )

        # Sort data for display
        if self.sort_by == "cardinality":
            df = df.sort_values(self.size_col, ascending=False)
        elif self.sort_by == "degree":
            df = df.assign(_degree=df[self.sets].sum(axis=1))
            df = df.sort_values(
                ["_degree", self.size_col], ascending=[True, False]
            ).drop(columns=["_degree"])
        # sort_by=None: preserve input order

        # Display only n first intersections if max_subsets is set
        if self.max_subsets is not None:
            df = df.head(self.max_subsets)

        return df.reset_index(drop=True)

    def _build_plots(self):
        """Build all panels. Called once during __init__."""
        self.p_bars = self._create_bar_panel()
        self.p_matrix = self._create_dot_matrix_panel()
        if self.show_totals:
            self.set_totals = self._compute_set_totals()
            self.p_totals = self._create_totals_panel()

    def _create_bar_panel(self):
        """Create the top intersection size bar chart."""
        data = ColumnDataSource(dict(
            x=self.x_coords,
            top=self.data[self.size_col].tolist(),
        ))

        fig = figure(
            x_range=self.x_coords,
            title=self.title,
            height=self.height_bars,
            width=self.width_matrix,
            output_backend="webgl",
            tools="save",
        )
        fig.toolbar.logo = None

        fig.vbar(x="x", top="top", width=0.6, source=data, color=self.bar_color)

        fig.add_tools(HoverTool(tooltips=[("", "@top")], mode="vline"))

        fig.xaxis.visible = False
        fig.xgrid.grid_line_color = None
        fig.yaxis.axis_label = self.bar_ylabel
        fig.yaxis.axis_label_text_font_style = "normal"
        fig.yaxis.formatter = CustomJSTickFormatter(
            code="""
            if (tick < 1000) {
                return tick.toFixed(0);
            } else {
                return (tick / 1000).toFixed(1) + 'k';
            }
        """)
        fig.y_range.start = 0
        fig.y_range.end = max(self.data[self.size_col].max() * 1.1, 10)
        fig.yaxis.minor_tick_line_color = None

        return fig

    def _create_dot_matrix_panel(self):
        """Create the dot matrix showing set membership per intersection."""
        n_sets = len(self.sets)

        inactive_x, inactive_y = [], []
        active_x, active_y = [], []
        seg_x, seg_top, seg_bottom = [], [], []

        for i, (_, row) in enumerate(self.data.iterrows()):
            active_ys = []
            for j, set_name in enumerate(self.sets):
                y_pos = n_sets - 1 - j
                is_active = bool(row[set_name])
                if is_active:
                    active_x.append(self.x_coords[i])
                    active_y.append(y_pos)
                    active_ys.append(y_pos)
                else:
                    inactive_x.append(self.x_coords[i])
                    inactive_y.append(y_pos)

            if len(active_ys) > 1:
                seg_x.append(self.x_coords[i])
                seg_top.append(max(active_ys))
                seg_bottom.append(min(active_ys))

        inactive_source = ColumnDataSource(dict(x=inactive_x, y=inactive_y))
        active_source = ColumnDataSource(dict(x=active_x, y=active_y))
        seg_source = ColumnDataSource(dict(x=seg_x, top=seg_top, bottom=seg_bottom))

        fig = figure(
            x_range=self.p_bars.x_range,
            y_range=Range1d(-0.5, n_sets - 0.5),
            height=self.height_matrix,
            width=self.width_matrix,
            output_backend="webgl",
            tools="save",
        )
        fig.toolbar.logo = None

        # inactive dots (below connectors and active dots)
        fig.scatter(
            x="x", y="y", size=14, color=self.inactive_dot_color,
            alpha=0.4, source=inactive_source
        )
        # Vertical connectors between active dots in each column
        fig.vbar(
            x="x", top="top", bottom="bottom", width=0.06,
            source=seg_source, color=self.dot_color
        )
        # active dots (on top)
        fig.scatter(
            x="x", y="y", size=14, color=self.dot_color,
            alpha=1.0, source=active_source
        )

        fig.xaxis.visible = False
        fig.xgrid.grid_line_color = None
        fig.ygrid.grid_line_color = None
        fig.yaxis.ticker = list(range(n_sets))
        fig.yaxis.major_label_overrides = {
            (n_sets - 1 - j): label
            for j, label in enumerate(self.sets)
        }

        # Calculate label width for y-axis of dot matrix to set appropriate left margin
        label_width = max(len(s) for s in self.sets) * 7
        fig.min_border_left = label_width

        return fig

    def _compute_set_totals(self):
        """Sum intersection sizes for each set across all intersections."""
        return {
            s: self.data.loc[self.data[s], self.size_col].sum()
            for s in self.sets
        }

    def _create_totals_panel(self):
        """Create the left-hand horizontal bar chart showing per-set totals."""
        # Reversed so the top set aligns with the top of the dot matrix
        labels_r = list(reversed(self.sets))
        values_r = [self.set_totals[s] for s in reversed(self.sets)]

        source = ColumnDataSource(
            dict(y=labels_r, left=values_r, right=[0] * len(values_r)))

        max_val = max(max(values_r) * 1.1, 10) if values_r else 10
        fig = figure(
            y_range=labels_r,
            x_range=Range1d(max_val, 0),
            height=self.height_matrix,
            width=self.width_totals,
            output_backend="webgl",
            tools="save",
        )
        fig.toolbar.logo = None

        fig.hbar(
            y="y", left="left", right="right", height=0.6,
            source=source, color=self.bar_color
        )

        fig.add_tools(HoverTool(tooltips=[("", "@left")]))

        fig.xaxis.minor_tick_line_color = None
        fig.xaxis.axis_label = self.totals_xlabel
        fig.xaxis.axis_label_text_font_style = "normal"
        fig.xaxis.formatter = CustomJSTickFormatter(code="""
            if (tick < 1000) {
                return tick.toFixed(0);
            } else {
                return (tick / 1000).toFixed(1) + 'k';
            }
        """)
        fig.yaxis.visible = False
        fig.ygrid.grid_line_color = None
        fig.min_border_right = 0

        return fig

    def _compose_grid(self):
        """Assemble panels into the final gridplot layout."""
        # Hide tools on all figures before merging
        for fig in [self.p_bars, self.p_matrix] + (
            [self.p_totals] if self.show_totals else []
        ):
            for tool in fig.toolbar.tools:
                if isinstance(tool, HoverTool):
                    tool.toggleable = False
        if self.show_totals:
            grid = gridplot(
                [[None, self.p_bars], [self.p_totals, self.p_matrix]],
                merge_tools=True,
                toolbar_location="right",
            )
        else:
            grid = gridplot(
                [[self.p_bars], [self.p_matrix]],
                merge_tools=True,
                toolbar_location="right",
            )
        grid.toolbar.logo = None
        return grid

    @property
    def total_height(self):
        """Total height of the plot in pixels."""
        return self.height_bars + self.height_matrix


def upsetplot(data, sets, **kwargs):
    """Functional alias for `UpSetPlot`."""
    return UpSetPlot(data, sets, **kwargs)
