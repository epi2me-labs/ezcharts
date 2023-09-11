"""Nextclade reporting section."""

import argparse

from dominate.tags import script
from dominate.util import raw

from ezcharts.components.reports.comp import ComponentReport
from ezcharts.components.theme import LAB_head_resources
from ezcharts.layout.base import Snippet
from ezcharts.layout.resource import ScriptResource
from ezcharts.layout.util import inline, render_template


class NextClade(Snippet):
    """A nextclade report component."""

    TAG = 'nxt-table'

    def __init__(
        self,
        json_path
    ) -> None:
        """Initialize a nextclade instance."""
        super().__init__(
            styles=None,
            classes=None)

        with open(json_path, encoding='utf8') as fh:
            data = fh.read()

        with self:
            script(raw(render_template(
                template=(
                    """
                    const data = {{ data }}
                    var nxt = document.querySelector('nxt-table')
                    window.addEventListener("load", () => {
                        nxt.data = data.results
                    })
                    """),
                data=data)))


NXTComponent = ScriptResource(
    path='nextclade.html',
    loader=inline)


def main(args):
    """Entry point to create a report from nextclade."""
    nxt = NextClade(args.json)
    report = ComponentReport(
        'Nextclade', nxt,
        head_resources=[*LAB_head_resources, NXTComponent])
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'Params table',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        "json",
        help="JSON output file from nextclade CLI."
    )
    parser.add_argument(
        "--output",
        default="nextclade_report.html",
        help="Output HTML file."
    )
    return parser
