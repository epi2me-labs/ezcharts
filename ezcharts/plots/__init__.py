"""Plotting functionality via echarts."""

import argparse

from pkg_resources import resource_filename

from ezcharts import util as ezutil
from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.plots import util
from ezcharts.plots._model import EChartsOption
from ezcharts.plots.util import JSCode


# NOTE: the add_x methods below allow for type checking that pydantic V1 would
#       otherwise not perform, e.g. plt.series.append({...}) evades checking
#       https://github.com/pydantic/pydantic/issues/496

_logger = ezutil.get_named_logger("Plotter")


class Formatter(util.JSCode):
    """Formatter for echarts axis labels."""

    def __init__(self):
        """Instantiate the class with some JS code.

        Convert high and low values to scientific notation.
        """
        jscode = """function(value, index){
                        if (value == 0){
                            return 0;
                        }
                        if (value > 10000 || value < 0.0001){
                            return value.toExponential();
                        }
                        else{
                            return value
                        }
                     }
        """
        super().__init__(jscode)


class Plot(EChartsOption):
    """Main plotting interface."""

    def __init__(self, *args, **kwargs):
        """Initialize a plot with defaults."""
        super().__init__(*args, **kwargs)
        self.toolbox = {
            "show": True,
            "feature": {
                "dataZoom": {"show": True},
                "dataView": {"readOnly": True},
                "restore": {},
                "saveAsImage": {}
            }
        }

    @property
    def logger(self):
        """Return logger for class."""
        return _logger

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

    def render_html(self, output, **kwargs):
        """Render plot to a file.

        :params output: output file.
        :param kwargs: passed to `EZChart`.
        """
        try:
            title = self.title.text
        except AttributeError:
            title = 'ezChart Plot'
        chart = EZChart(self, 'epi2melabs', **kwargs)
        report = ComponentReport(title, chart)
        report.write(output)

    def finalise(self):
        """Apply a standard set of defaults to patch eCharts.

        Prevent overlap of axis name with labels and other things.
        """
        self.fix_axis_labels()

    def fix_axis_labels(self):
        """Try to place axis labels so they don't overlap tick labels."""
        if hasattr(self, 'grid') and self.grid is not None:
            self.logger.warning(
                "Cannot correct axis labels in complicated scenarios.")
            return

        # we only try to fix up axes if we have one, else we don't
        # really know what's going on
        axes = list()
        if not isinstance(self.xAxis, list):
            axes.append([self.xAxis, 0])
        if not isinstance(self.xAxis, list):
            axes.append([self.yAxis, 1])

        # to make space for axis labels we shrink the plot by setting a grid
        # and changing the margins of its sole component
        self.grid = dict()

        for axis, data_idx in axes:
            # TODO: is data_idx always 0/1 for x/y?
            axis.nameLocation = 'middle'  # 'cos eCharts its weird

            if axis.axisLabel is not None:
                axis.axisLabel.formatter = Formatter()
            else:
                axis.axisLabel = {
                    "formatter": Formatter()}

            if axis == self.yAxis:
                name_offset = 45
                self.grid.left = 55

            elif axis == self.xAxis:
                name_offset = 25
                if axis.type == 'category':
                    # Warning: Just taking the raw datasource here.
                    # Any plots with transformed data may not have axes setup
                    # correctly
                    num_label_digits = max((
                        len(str(x[data_idx]))
                        for x in self.dataset[0].source))
                    try:
                        rotation = axis.axisLabel.rotate
                    except AttributeError:
                        rotation = 0
                    if rotation != 0:  # Let's assume a sensible rotation of 45
                        name_offset = 25 + num_label_digits * 4
                        self.grid.bottom = name_offset + 15

            axis.nameGap = name_offset

        return self


def main(args):
    """Entry point to demonstrate an ezChart."""
    plt = Plot.parse_file(args.plot_spec)
    plt.render_html(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'ezChart Demo',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--plot_spec",
        default=resource_filename('ezcharts', "data/test/plot-spec.json"),
        help=(
            "A JSON file defining an eCharts plot",
            "key/values."
        ))
    parser.add_argument(
        "--output",
        default="ezcharts_plot_report.html",
        help="Output HTML file.")
    return parser
