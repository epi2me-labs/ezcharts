"""Simple eCharts API."""

__version__ = "0.0.1"

import argparse
import importlib
import json

import pyecharts

from ezcharts.types import SetOptions


class Plot(pyecharts.charts.base.Base):
    """Main plotting interface."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super().__init__(*args, **kwargs)
        # we can't just subclass because fields conflict. (And this
        # is cleaner, not like bokeh attaching things everywhere).
        self.opt = SetOptions(parent=self)

    class Encoder(json.JSONEncoder):
        """JSON encoder of self."""

        def default(self, obj):
            """Return a boring message."""
            return "A Plot"

    def to_json(self, **kwargs):
        """Create a json representation of options."""
        return json.dumps(self.opt, cls=self.Encoder, **kwargs)


def cli():
    """Run ezcharts entry point."""
    parser = argparse.ArgumentParser(
        'ezcharts',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-v', '--version', action='version',
        version='%(prog)s {}'.format(__version__))

    subparsers = parser.add_subparsers(
        title='subcommands', description='valid commands',
        help='additional help', dest='command')
    subparsers.required = True

    # add reporting modules
    modules = ['demo']
    for module in modules:
        mod = importlib.import_module('ezcharts.components.{}'.format(module))
        p = subparsers.add_parser(module, parents=[mod.argparser()])
        p.set_defaults(func=mod.main)

    args = parser.parse_args()
    args.func(args)
