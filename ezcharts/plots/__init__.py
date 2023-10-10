"""Plotting functionality via echarts."""


from bokeh.plotting import figure
import pandas as pd
import sigfig

from ezcharts import util as ezutil
from ezcharts.plots import util
from ezcharts.plots._model import EChartsOption
from ezcharts.plots.util import JSCode

# NOTE: the add_x methods below allow for type checking that pydantic V1 would
#       otherwise not perform, e.g. plt.series.append({...}) evades checking
#       https://github.com/pydantic/pydantic/issues/496


class AxisLabelFormatter(JSCode):
    """Formatter for echarts axis labels."""

    def __init__(self, sci_notation=(0.001, 10000)):
        """Init.

        :param: sci_notation:
            True: use scientific notation for the axis.
            False: use raw values for the axis.
            tuple: Upper and lower limits for determining use of scientific notation.
        """
        self.sci_notation = sci_notation

    def apply(self, values=None):
        """
        Create the JS formatter.

        Use the values from the axis to dertermine if scientific notation
        or raw values will be used. If values is None, use raw values as this is
        likely a category axis.

        :param values: The raw values from the current axis.
        """
        self.jscode = """function(value, index){
                        if (value == 0){
                            return 0;
                        }
                        if (@use_sci == 'false'){
                            return value;
                        }
                        if (@use_sci == 'true'){
                            return value.toExponential();
                        }
                     }
        """
        if values is None:
            use_sci = False
        else:
            if self.sci_notation is True:
                use_sci = True
            elif self.sci_notation is False:
                use_sci = False
            else:
                # If the value with the largest magnitude (in other words, the largest
                # positive or negative value or value furthest from zero) falls outside
                # the limits, convert all to sci_notation.
                sci_limits = self.sci_notation
                v = max(abs(min(values)), max(values))
                if v < sci_limits[0] or v > sci_limits[1]:
                    use_sci = True
                else:
                    use_sci = False
        super().__init__(self.jscode.replace('@use_sci', f"'{str(use_sci).lower()}'"))
        return use_sci


class Plot(EChartsOption):
    """EChart plotting interface."""

    _logger = ezutil.get_named_logger("EChrtPlotr")

    def __init__(self, *args, **kwargs):
        """Initialize a plot with defaults."""
        super().__init__(*args, **kwargs)
        self.toolbox = {
            "show": True,
            "feature": {
                "dataZoom": {"show": True},
                "dataView": {"readOnly": False},
                "restore": {},
                "saveAsImage": {}
            }
        }

    @property
    def logger(self):
        """Return logger for class."""
        return self._logger

    def add_series(self, spec):
        """Add a series to chart."""
        orig = self.series
        self.series = [spec]  # validates new entry
        if orig is not None:
            self.series = orig + self.series

    def add_dataset(self, spec):
        """Add a dataset to a chart."""
        orig = self.dataset
        self.dataset = [spec]  # validates new entry
        if orig is not None:
            self.dataset = orig + self.dataset

    def to_json(self, **kwargs):
        """Create a json representation of options.

        Here we clean up the serialised json in the event that it includes
        any javascript code.
        """
        self.finalise()
        return JSCode._clean(self.json(exclude_unset=True))

    def finalise(self):
        """Apply a standard set of defaults to patch eCharts.

        Prevent overlap of axis name with labels and other things.
        """
        self.fix_axis_labels()

    def _axes_dimensions(self):
        """Get axes for each dimension."""
        axes = list()
        if not isinstance(self.xAxis, list):
            axes.append([self.xAxis, 0])
        if not isinstance(self.yAxis, list):
            axes.append([self.yAxis, 1])
        return axes

    def fix_axis_labels(self):
        """Try to place axis labels so that they don't overlap tick labels."""
        if hasattr(self, 'grid') and self.grid is not None:
            self.logger.warning(
                "Cannot correct axis labels in complicated scenarios.")
            return

        # we only try to fix up axes if we have one, else we don't
        # really know what's going on
        axes = self._axes_dimensions()

        # to make space for axis labels we shrink the plot by setting a grid
        # and changing the margins of its sole component
        self.grid = dict()

        for axis, data_idx in axes:
            axis.nameLocation = 'middle'  # 'cos eCharts its weird

            # Get all the raw values from each dataset that contains a source.
            # Warning: Just taking the raw datasource here.
            # Any plots with transformed data may not have axes setup correctly.
            raw_vals = []
            for ds in self.dataset:
                if ds.source is not None:
                    # `ds.source` could be a numpy array or just a list of lists; we'll
                    # transform it into a `pd.DataFrame` so that we can do column-wise
                    # indexing while preserving dtypes
                    raw_vals.extend(pd.DataFrame(ds.source).iloc[:, data_idx])

            # Allow formatter to be set by user.
            if axis.axisLabel is None:
                axis.axisLabel = dict(formatter=AxisLabelFormatter())
            elif axis.axisLabel.formatter is None:
                axis.axisLabel.formatter = AxisLabelFormatter()

            if axis.type == 'value':
                is_sci = axis.axisLabel.formatter.apply(raw_vals)
                # If using sci. notation, there will be 4-5 characters in the label
                if is_sci:
                    max_n_label_digits = 5
                else:
                    round_vals = [
                        sigfig.round(val, sigfigs=1) for val in raw_vals]
                    max_n_label_digits = max([len(str(x)) for x in round_vals])
            else:
                axis.axisLabel.formatter.apply()
                max_n_label_digits = max([len(str(x)) for x in raw_vals])

            if axis == self.xAxis:
                name_offset = 25
                try:
                    rotation = axis.axisLabel.rotate
                except AttributeError:
                    rotation = 0
                if rotation != 0:  # Let's assume a sensible rotation of 45
                    # Rotation makes axis labels project downwards more
                    name_offset = 25 + max_n_label_digits * 4
                    self.grid.bottom = name_offset + 15

            elif axis == self.yAxis:
                name_offset = 20 + max_n_label_digits * 6
                self.grid.left = name_offset + 10

            axis.nameGap = name_offset

        return self


class _HistogramPlot(Plot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _axes_dimensions(self):
        """Get correct axes for histograms.

        For histograms, the first two dataset columns are start/stop
        rectangle x coords. The third column contains bar heights.
        """
        return [self.xAxis, 1], [self.yAxis, 2]


class BokehPlot:
    """Plotting interface for Bokeh."""

    _logger = ezutil.get_named_logger("BokehPlotr")
    colors = util.choose_palette()
    tools = "hover,crosshair,pan,box_zoom,zoom_in,zoom_out,reset,save"

    def __init__(self, *args, **kwargs):
        """Initialize a bokeh figure."""
        defaults = dict(
            output_backend="webgl",
            tools=self.tools,
            height=300,
            width=600,
        )
        defaults.update(kwargs)
        self._fig = figure(*args, **defaults)
        # remove Bokeh logo
        self._fig.toolbar.logo = None

    @property
    def logger(self):
        """Return logger for class."""
        return self._logger


class _NoAxisFixPlot(Plot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def fix_axis_labels(self):
        self.logger.warning("Skipping axis label fixing")
