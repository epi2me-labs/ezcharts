"""Entrypoint to demo an ezCharts plot."""
import argparse

from pkg_resources import resource_filename

from ezcharts.components.reports.comp import ComponentReport
from ezcharts.plots import Plot


def main(args):
    """Entry point to demonstrate an ezChart."""
    plt = Plot.parse_file(args.plot_spec)
    ComponentReport.from_plot(plt, args.output)


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
