"""Plotting functionality via echarts."""

import argparse

from pkg_resources import resource_filename

from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.plots._model import EChartsOption


# NOTE: the add_x methods below allow for type checking that pydantic V1 would
#       otherwise not perform, e.g. plt.series.append({...}) evades checking
#       https://github.com/pydantic/pydantic/issues/496


class Plot(EChartsOption):
    """Main plotting interface."""

    def to_json(self, **kwargs):
        """Create a json representation of options."""
        return self.json(exclude_unset=True)

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

    def render_html(self, output):
        """Render plot to a file.

        :params output: output file.
        """
        try:
            title = self.title.text
        except AttributeError:
            title = 'ezChart Plot'
        chart = EZChart(self, 'epi2melabs')
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
        default=resource_filename('ezcharts', "test_data/plot-spec.json"),
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
