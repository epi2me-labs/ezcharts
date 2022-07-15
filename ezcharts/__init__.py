"""Simple eCharts API."""

import argparse
import importlib

__version__ = "0.0.1"


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
