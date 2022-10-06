"""Simple eCharts API."""

__version__ = "0.2.2"

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

    # all component demos, plus some others
    components = ['params', 'nextclade']
    others = ['ezcharts.demo', 'ezcharts.plots', 'ezcharts.plots.ideogram']

    demos = [f'ezcharts.components.{comp}' for comp in components] + others
    for module in demos:
        mod = importlib.import_module(module)
        p = subparsers.add_parser(
            module.split(".")[-1], parents=[mod.argparser()])
        p.set_defaults(func=mod.main)

    args = parser.parse_args()
    args.func(args)
