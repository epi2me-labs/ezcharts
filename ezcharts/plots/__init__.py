"""Plotting functionality via echarts."""

import argparse

from pkg_resources import resource_filename

from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.plots._model import EChartsOption
from ezcharts.plots.util import JSCode


# NOTE: the add_x methods below allow for type checking that pydantic V1 would
#       otherwise not perform, e.g. plt.series.append({...}) evades checking
#       https://github.com/pydantic/pydantic/issues/496


class Plot(EChartsOption):
    """Main plotting interface."""

    def to_json(self, **kwargs):
        """
        Create a json representation of options.

        Here we clean up the serialised json in the event that it includes
        any javascript code.
        """
        return JSCode._clean(self.json(exclude_unset=True))

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


def main(args):
    """Entry point to demonstrate an ezChart."""
    plt = Plot.parse_file(args.plot_spec)
    plt.render_html(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'ezChart Demo',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        "--plot_spec",
        default=resource_filename('ezcharts', "test/plot-spec.json"),
        help=(
            "A JSON file defining an eCharts plot",
            "key/values."
        )
    )
    parser.add_argument(
        "--output",
        default="ezchart_plot_report.html",
        help="Output HTML file."
    )
    return parser
