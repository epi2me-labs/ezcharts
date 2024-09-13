"""A reusable workflow params table."""
import argparse
import json
import os

from pkg_resources import resource_filename

from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.snippets.table import DataTable


class ParamsTable(DataTable):
    """Display workflow params."""

    def __init__(
        self,
        params_file: str,
        **kwargs
    ) -> None:
        """Create table."""
        if not os.path.isfile(params_file):
            raise IOError('`params` should be a JSON file.')
        super().__init__(['Key', 'Value'], **kwargs)

        DISALLOWED_KEYS = {
            "help",
            "version",
            "wf",
            "aws_image_prefix",
            "aws_queue",
            "schema_ignore_params",
            "show_hidden_params",
            "monochrome_logs",
            "validate_params",
            "disable_ping",
        }

        with open(params_file, encoding='utf-8') as f:
            data = json.load(f)
            with self.body:
                for k, v in data.items():
                    if isinstance(v, str) and v.startswith("s3://"):
                        v = '/'.join(v.replace("s3://", "").split("/")[2:])
                    if k not in DISALLOWED_KEYS:
                        self.add_row(title=None, columns=[k, str(v)])


def main(args):
    """Entry point to demonstrate a parameter table."""
    comp_title = 'Parameter Table'
    param_table = ParamsTable(args.params)
    report = ComponentReport(comp_title, param_table)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'Params table',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        "--params",
        default=resource_filename('ezcharts', "test/params.json"),
        help=(
            "A JSON file containing the workflow parameter "
            "key/values."
        )
    )
    parser.add_argument(
        "--output",
        default="params_table_report.html",
        help="Output HTML file."
    )
    return parser
