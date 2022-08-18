"""Simple eCharts API."""

__version__ = "0.0.1"

import argparse
import importlib

from ezcharts.plots.axisgrid import *  # noqa: F401,F403
from ezcharts.plots.categorical import *  # noqa: F401,F403
from ezcharts.plots.distribution import *  # noqa: F401,F403
from ezcharts.plots.matrix import *  # noqa: F401,F403
from ezcharts.plots.regression import *  # noqa: F401,F403
from ezcharts.plots.relational import *  # noqa: F401,F403


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

    # add demo module
    demo_module = importlib.import_module('ezcharts.demo')
    p = subparsers.add_parser('demo', parents=[demo_module.argparser()])
    p.set_defaults(func=demo_module.main)

    # add component modules
    modules = ['params']
    for module in modules:
        mod = importlib.import_module('ezcharts.components.{}'.format(module))
        p = subparsers.add_parser(module, parents=[mod.argparser()])
        p.set_defaults(func=mod.main)

    args = parser.parse_args()
    args.func(args)
