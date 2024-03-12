"""Simple eCharts API."""

__version__ = "0.7.10"

import argparse
import importlib
import logging

from ezcharts import util
from ezcharts.plots.axisgrid import *  # noqa: F401,F403
from ezcharts.plots.categorical import *  # noqa: F401,F403
from ezcharts.plots.distribution import *  # noqa: F401,F403
from ezcharts.plots.matrix import *  # noqa: F401,F403
from ezcharts.plots.metagenomics_sankey import *  # noqa: F401,F403
from ezcharts.plots.regression import *  # noqa: F401,F403
from ezcharts.plots.relational import *  # noqa: F401,F403
from ezcharts.plots.sunburst import *  # noqa: F401,F403


def cli():
    """Run ezcharts entry point."""
    parser = argparse.ArgumentParser(
        'ezcharts',
        parents=[util._log_level()],
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-v', '--version', action='version',
        version='%(prog)s {}'.format(__version__))

    subparsers = parser.add_subparsers(
        title='subcommands', description='valid commands',
        help='additional help', dest='command')
    subparsers.required = True

    # all component demos, plus some others
    components = [
        'params', 'nextclade', 'fastcat', 'dss',
        'modkit', 'mosdepth', 'clinvar', 'bcfstats'
        ]
    others = ['ezcharts.demo', 'ezcharts.plots.demo', 'ezcharts.plots.ideogram']

    demos = [f'ezcharts.components.{comp}' for comp in components] + others
    for module in demos:
        mod = importlib.import_module(module)
        subparser_name = module.split(".")[-1]
        if module == 'ezcharts.plots.demo':
            subparser_name = 'plots'
        p = subparsers.add_parser(
            subparser_name, parents=[mod.argparser()])
        p.set_defaults(func=mod.main)

    args = parser.parse_args()
    logging.basicConfig(
        format='[%(asctime)s - %(name)s] %(message)s',
        datefmt='%H:%M:%S', level=logging.INFO)
    logging.captureWarnings(True)
    logger = logging.getLogger(__package__)
    logger.setLevel(args.log_level)

    args.func(args)
