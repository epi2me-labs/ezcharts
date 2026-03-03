"""Sequence analysis components for genomics workflows."""

from bokeh.layouts import column
from bokeh.models import (
    ColumnDataSource,
    CustomJSTickFormatter,
    FixedTicker,
    LabelSet,
    Range1d,
    Span,
    WheelZoomTool
)
from bokeh.plotting import figure

from ezcharts.plots import BokehPlot


# Base color mapping for nucleotides
NUCLEOTIDE_COLORS = {
    "A": "#0084A9",
    "T": "#F5CC49",
    "G": "#17BB75",
    "C": "#EF4135",
    "DEL": "#003E5E",
    "-": "#003E5E"
}


class BaseComposition(BokehPlot):
    """
    Multi-panel interactive visualization for sequence base composition analysis.

    Creates a linked view of:
    - Coverage depth track
    - Consensus quality scores
    - Base composition as stacked barplots

    All panels share synchronized X-axis for coordinated zooming and panning.
    """

    def __init__(
        self,
        data,
        position='x',
        coverage='COV',
        reference_base='reference_base',
        consensus_base=None,
        qscore=None,
        qscore_threshold=30,
        base_columns=None,
        nucleotide_colors=None,
        color='#007FA9',
        show_coverage=True,
        show_qscore=True,
        show_composition=True,
        height_coverage=150,
        height_qscore=150,
        height_composition=150,
        view_range=None,
        plotting_range=None,
        coverage_low_threshold=10,
        coverage_unique_threshold=6,
        coverage_high_threshold=1000
    ):
        """
        Initialize base composition visualization.

        Parameters
        ----------
        data : pd.DataFrame
            Consolidated dataframe with sequence information.
        position : str, default 'x'
            Column name for position along sequence.
        coverage : str, default 'COV'
            Column name for coverage values.
        reference_base : str, default 'reference_base'
            Column name for reference sequence bases.
        consensus_base : str, optional
            Column name for consensus sequence bases.
        qscore : str, optional
            Column name for quality scores.
        qscore_threshold : float, default 30
            Threshold for Q-score reference line.
        base_columns : list, optional
            Base count column names. Default: ['A', 'T', 'G', 'C', 'DEL']
        nucleotide_colors : dict, optional
            Color mapping dictionary for nucleotides,
            e.g. {'A': '#0084A9', 'T': '#F5CC49', ...}.
            If not provided, uses default colors.
        color : str, default '#007FA9'
            Primary color for plots.
        show_coverage : bool, default True
            Whether to show coverage panel.
        show_qscore : bool, default True
            Whether to show Q-score panel.
        show_composition : bool, default True
            Whether to show composition panel.
        height_coverage : int, default 150
            Height in pixels for coverage plot.
        height_qscore : int, default 150
            Height in pixels for Q-score plot.
        height_composition : int, default 150
            Height in pixels for composition plot.
        view_range : Range1d, optional
            Initial X-axis range visible.
        plotting_range : tuple of (int, int), optional
            Range of positions to display as (start, end). If provided,
            only data within this range (inclusive) will be plotted.
        coverage_low_threshold : int, default 10
            Maximum coverage value for using FixedTicker with exact values.
            For coverage below this threshold with few unique values,
            Y-axis ticks will show only the exact coverage values present.
        coverage_unique_threshold : int, default 6
            Maximum number of unique coverage values for using FixedTicker.
            Works in combination with coverage_low_threshold.
        coverage_high_threshold : int, default 1000
            Minimum coverage value for using 'k' suffix formatting.
            Coverage values >= this threshold will be shown as '1k', '2.5k', etc.
        """
        self.original_data = data.copy()  # Keep original data before filtering
        self.data = data.copy()
        self.position = position
        self.coverage = coverage
        self.reference_base = reference_base
        self.consensus_base = consensus_base
        self.qscore = qscore
        self.qscore_threshold = qscore_threshold
        self.base_columns = base_columns or ['A', 'T', 'G', 'C', 'DEL']
        self.nucleotide_colors = nucleotide_colors or NUCLEOTIDE_COLORS
        self.color = color
        self.show_coverage = show_coverage
        self.show_qscore = show_qscore
        self.show_composition = show_composition
        self.height_coverage = height_coverage
        self.height_qscore = height_qscore
        self.height_composition = height_composition
        self.coverage_low_threshold = coverage_low_threshold
        self.coverage_unique_threshold = coverage_unique_threshold
        self.coverage_high_threshold = coverage_high_threshold

        # Validate existence of required columns
        self._validate_data()
        self._validate_display_options()

        # Subset a range of data for plotting
        self.plotting_range = plotting_range
        if plotting_range is not None:
            self._filter_plotting_range()

        self._prepare_data()

        # Set view_range visible initially
        if view_range is None:
            padding = 0.5  # Prevents clipped bars at the edges of the plot
            if plotting_range is not None:
                start, end = plotting_range
                range_width = end - start
                initial_view_width = max(10, min(range_width, 100))
                view_range = Range1d(
                    start - padding,
                    start + initial_view_width + padding,
                    bounds=(start - padding, end + padding)
                )
            else:
                initial_view_width = max(10, min(100, len(self.data)))
                view_range = Range1d(
                    0, initial_view_width + padding,
                    bounds=(0, len(self.data) + padding)
                )
        else:
            # User provided custom view_range
            if plotting_range is not None:
                valid_min, valid_max = plotting_range
                padding = 0.5  # Prevents clipped bars at the edges of the plot
            else:
                valid_min = 0
                valid_max = len(self.data)
                padding = 2  # Original padding for full dataset

            # Check view_range is valid (start < end)
            if view_range.start >= view_range.end:
                raise ValueError(
                    f"Invalid view_range: start ({view_range.start}) must be "
                    f"less than end ({view_range.end})"
                )
            # Check view_range is completely within valid range
            if view_range.start < valid_min or view_range.end > valid_max:
                raise ValueError(
                    f"view_range ({view_range.start}, {view_range.end}) must be "
                    f"within the plotting range ({valid_min}, {valid_max})"
                )

            # Apply padding and set bounds
            view_range = Range1d(
                view_range.start - padding,
                view_range.end + padding,
                bounds=(
                    valid_min - padding if plotting_range is not None else valid_min,
                    valid_max + padding
                )
            )
        self.view_range = view_range

        # Build the visualization
        self._build_plots()
        # Show toolbar only on first plot
        self._configure_toolbars()
        # Add range boundary ticks if plotting_range specified
        self._add_range_ticks()
        # Initialize parent BokehPlot
        super().__init__()
        self._fig = column(*self.plots, sizing_mode="stretch_both")

    def _validate_data(self):
        """Validate input data has required columns."""
        # Ensure position column exists
        if self.position not in self.data.columns:
            if 'x' not in self.data.columns:
                self.data['x'] = self.data.index + 1
                self.position = 'x'
            else:
                raise ValueError(f"Position column '{self.position}' not found")
        # Check required columns exist
        required = []
        if self.show_coverage:
            required.append(self.coverage)
        if self.show_composition:
            required.append(self.reference_base)
            required.extend(self.base_columns)
        missing = [col for col in required if col not in self.data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def _validate_display_options(self):
        """Validate that at least one plot panel is enabled."""
        if not any([self.show_coverage, self.show_qscore, self.show_composition]):
            raise ValueError(
                "At least one plot must be enabled. "
                "show_coverage, show_qscore, and show_composition cannot all be False."
            )

    def _filter_plotting_range(self):
        """Filter data based on plotting_range."""
        if self.plotting_range is None:
            return
        start, end = self.plotting_range
        if start > end:
            raise ValueError(
                f"Invalid plotting_range ({start}, {end}): "
                f"start must be <= end"
            )
        # Filter data to specified range
        mask = (self.data[self.position] >= start) & (self.data[self.position] <= end)
        self.data = self.data[mask].copy()
        # Check if filtering resulted in empty dataset
        if len(self.data) == 0:
            raise ValueError(
                f"plotting_range ({start}, {end}) resulted in empty dataset. "
                f"Position range in data: "
                f"{self.original_data[self.position].min()}-"
                f"{self.original_data[self.position].max()}"
            )

    def _prepare_data(self):
        """Prepare data for plotting."""
        # Check if qscore should be shown
        self.has_qscore = (
            self.qscore is not None
            and self.qscore in self.data.columns
            and self.show_qscore
        )
        # Add color columns for labels
        if self.show_composition and self.reference_base in self.data.columns:
            self.data['reference_color'] = self.data[self.reference_base].map(
                self.nucleotide_colors
            ).fillna('#666666')
        if (
            self.has_qscore
            and self.consensus_base
            and self.consensus_base in self.data.columns
        ):
            self.data['consensus_color'] = self.data[self.consensus_base].map(
                self.nucleotide_colors
            ).fillna('#666666')

    def _build_plots(self):
        """Build all plot panels."""
        self.plots = []

        # 1. Coverage plot
        if self.show_coverage:
            self.coverage_plot = self._create_coverage_plot()
            self.plots.append(self.coverage_plot)

        # 2. Q-score plot
        if self.has_qscore:
            self.qscore_plot = self._create_qscore_plot()
            self.plots.append(self.qscore_plot)

        # 3. Base composition plot
        if self.show_composition:
            self.composition_plot = self._create_composition_plot()
            self.plots.append(self.composition_plot)

    def _configure_toolbars(self):
        """Configure toolbars - show only on the first plot."""
        if len(self.plots) > 0:
            # Show toolbar only on first plot
            self.plots[0].toolbar_location = "above"
            # Hide toolbars on all other plots
            for plot in self.plots[1:]:
                plot.toolbar_location = None

    def _add_range_ticks(self):
        """Add tick marks for plotting_range start/end positions."""
        if self.plotting_range is None:
            return
        start, end = self.plotting_range
        # Add custom ticks to show range boundaries
        if len(self.plots) > 0:
            bottom_plot = self.plots[-1]
            # Create ticks at range boundaries and intermediate points
            range_width = end - start
            if range_width <= 20:
                tick_values = list(range(start, end + 1))
            elif range_width <= 100:
                tick_values = (
                    [start] + list(range(start + 10 - (start % 10), end, 10)) + [end])
            else:
                tick_values = (
                    [start] + list(range(start + 50 - (start % 50), end, 50)) + [end])
            tick_values = sorted(set(tick_values))
            bottom_plot.xaxis.ticker = FixedTicker(ticks=tick_values)
            bottom_plot.xaxis.visible = True

    def _create_coverage_plot(self):
        """Create coverage line plot."""
        plot = figure(
            x_range=self.view_range,
            height=self.height_coverage,
            title="Coverage of each position",
            tools=['xwheel_zoom', 'xpan', 'reset'],
            active_scroll='xwheel_zoom',
            output_backend="webgl"
        )

        plot.line(
            x=self.position,
            y=self.coverage,
            source=self.data,
            line_width=2,
            color=self.color
        )

        # Format Y-axis
        plot.y_range.start = 0
        unique_cov = self.data[self.coverage].dropna().unique()
        max_cov = self.data[self.coverage].max() if len(unique_cov) > 0 else 1
        # Only use FixedTicker for very low coverage to avoid duplicate labels
        if (
            max_cov < self.coverage_low_threshold and
            len(unique_cov) <= self.coverage_unique_threshold
        ):
            unique_cov.sort()
            plot.yaxis.ticker = FixedTicker(ticks=unique_cov.tolist())
        elif max_cov >= self.coverage_high_threshold:
            plot.yaxis.formatter = CustomJSTickFormatter(code="""
                if (tick < 1000) {
                    return tick.toFixed(0);
                } else {
                    return (tick / 1000).toFixed(1) + 'k';
                }
            """)
        # Otherwise let Bokeh handle ticks automatically

        plot.sizing_mode = 'scale_width'
        plot.xaxis.visible = False
        plot.yaxis.minor_tick_line_color = None
        plot.toolbar.logo = None

        wheel_zoom = plot.select_one(WheelZoomTool)
        if wheel_zoom:
            wheel_zoom.maintain_focus = False

        return plot

    def _create_qscore_plot(self):
        """Create Q-score bar plot."""
        plot = figure(
            x_range=self.view_range,
            height=self.height_qscore,
            title="Medaka consensus Q-score per base (Per-base Q-score, consensus base shown, position relative to the MSA)",  # noqa: E501
            tools=['xwheel_zoom', 'xpan', 'reset'],
            active_scroll='xwheel_zoom',
            output_backend="webgl"
        )

        plot.vbar(
            x=self.position,
            top=self.qscore,
            line_color="#FFFFFF",
            source=self.data[[self.position, self.qscore]],
            color=self.color
        )

        label_y_position = -7.5
        label_font_size = 12  # approx 1.5 units in plot
        y_range_margin = 1.5  # padding to allow space for labels

        # Add consensus base labels if available
        if self.consensus_base and self.consensus_base in self.data.columns:
            plot.add_layout(LabelSet(
                x=self.position,
                y=label_y_position,
                text=self.consensus_base,
                source=ColumnDataSource(
                    self.data[[self.position, self.consensus_base, 'consensus_color']]
                ),
                angle=0,
                text_color="consensus_color",
                text_align="center",
                text_font_size=f"{label_font_size}px",
                text_font_style="bold"
            ))

        # Same q_threshold variable to calculate percentage bases above Q score
        hline = Span(
            location=self.qscore_threshold,
            dimension='width',
            line_color='#3b3b3b',
            line_width=3
        )
        plot.renderers.extend([hline])

        plot.y_range.start = label_y_position - y_range_margin
        plot.sizing_mode = 'scale_width'
        plot.xaxis.visible = False
        plot.yaxis.minor_tick_line_color = None
        plot.toolbar.logo = None

        wheel_zoom = plot.select_one(WheelZoomTool)
        if wheel_zoom:
            wheel_zoom.maintain_focus = False

        return plot

    def _create_composition_plot(self):
        """Create stacked bar plot for base composition."""
        # Calculate proportions
        base_counts = self.data[self.base_columns]
        proportions = base_counts.div(base_counts.sum(axis=1), axis=0)

        # Prepare data for stacked bars
        vbar_data = proportions.to_dict(orient="list")
        vbar_data[self.position] = self.data[self.position].tolist()

        # Create plot
        plot = figure(
            x_range=self.view_range,
            height=self.height_composition,
            title="Base composition of each position (Proportion, reference base shown, position relative to the MSA)",  # noqa: E501
            toolbar_location=None,
            tools=['xwheel_zoom', 'xpan', 'reset'],
            active_scroll='xwheel_zoom',
            output_backend="webgl"
        )

        # Stacked bars
        colors = [
            self.nucleotide_colors.get(base, '#666666')
            for base in self.base_columns
        ]
        plot.vbar_stack(
            self.base_columns,
            x=self.position,
            color=colors,
            width=0.9,
            source=vbar_data,
            legend_label=self.base_columns
        )

        label_y_position = -0.2
        label_font_size = 12  # approx 1.5 units in plot
        y_range_margin = 0.01  # padding to allow space for labels

        # Add reference base labels
        plot.add_layout(LabelSet(
            x=self.position,
            y=label_y_position,
            text=self.reference_base,
            source=ColumnDataSource(
                self.data[[self.position, self.reference_base, 'reference_color']]
            ),
            angle=0,
            text_color="reference_color",
            text_align="center",
            text_font_size=f"{label_font_size}px",
            text_font_style="bold"
        ))

        plot.y_range.start = label_y_position - y_range_margin
        plot.y_range.end = 1.1
        plot.sizing_mode = 'scale_width'
        plot.yaxis.visible = False
        plot.xgrid.grid_line_color = None
        plot.ygrid.grid_line_color = None
        plot.xaxis.axis_line_color = "#E5E8E8"
        plot.outline_line_color = None
        plot.add_layout(plot.legend[0], 'right')
        plot.toolbar.logo = None

        wheel_zoom = plot.select_one(WheelZoomTool)
        if wheel_zoom:
            wheel_zoom.maintain_focus = False

        return plot
