"""An ezcharts component for making a sample status table."""

import argparse

from natsort import natsorted
import pandas as pd

from ezcharts import util
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets.table import DataTable


class StatusTable(Snippet):
    """Display a table of sample status."""

    logger = util.get_named_logger("StatusTable")

    def __init__(
        self,
        samples,
        sort_samples=True,
        **kwargs
    ) -> None:
        """Create sample status component.

        :param samples: list of samples.
        :param sort_samples: if True, samples will be sorted.
        """
        super().__init__(styles=None, classes=None, **kwargs)
        self.df = pd.DataFrame(index=samples)

        self.status = {}
        self.status_messages = {}

        if sort_samples:
            self.sample_order = natsorted(samples)
        else:
            self.sample_order = samples

    def add_column(self, col_name, add_dict):
        """Add a column from a dictionary of sample:value pairs.

        :param col_name: name of column to add
        :param add_dict: dictionary of sample:value pairs
        """
        if col_name in self.df.columns:
            self.logger.warning(f"Warning: Column {col_name} will be overwritten.")
        self.df[col_name] = pd.Series(add_dict)

    def add_badge_column(self, col_name, statuses, messages=None):
        """Add a column with values formatted as badges.

        :param col_name: name of column to add
        :param statuses: dictionary of sample: status,
            where status is a boolean that will be converted
            to a styled pass or fail badge
        :param messages: dictionary of sample: message,
            the message will be added to the status badge
        """
        if col_name in self.df.columns:
            self.logger.warning(f"Warning: Column {col_name} will be overwritten.")
        if messages is None:
            messages = {}
        self.df[col_name] = None
        for sample in self.df.index:
            self.df.at[sample, col_name] = self.format_badge(
                statuses.get(sample, None),
                messages.get(sample, None))

    def set_status(self, sample, status, message=None):
        """Set the status of a sample."""
        self.status[sample] = status
        self.status_messages[sample] = message

    def write_table(self):
        """Write the sample status table."""
        # Add a status column
        self.add_badge_column("Status", self.status, self.status_messages)
        # Move status column to the start
        self.df = self.df[
            ["Status"] + [col for col in self.df.columns if col != "Status"]
        ]

        self.df.fillna("-", inplace=True)

        self.df = self.df.reset_index().rename(columns={"index": "Sample"})

        # Sort the samples
        self.df = self.df.assign(
            Sample=lambda x: pd.Categorical(
                x["Sample"],
                categories=self.sample_order,
                ordered=True
            )
        ).sort_values("Sample")

        # Write table
        DataTable.from_pandas(self.df, use_index=False)

    @staticmethod
    def format_badge(status, message=None):
        """Format badge, green for success, red for failure."""
        badge_classes = ["badge", "badge-icon-solid", "rounded-pill", "p-2"]
        if status is None:
            badge_classes.append("badge-neutral-solid")
            if not message:
                message = "No status"
        elif status is True:
            badge_classes.append("badge-pass-solid")
            if not message:
                message = "Pass"
        else:
            badge_classes.append("badge-fail-solid")
            if not message:
                message = "Fail"
        return f'<span class="{" ".join(badge_classes)}">' + message + '</span>'


def main(args):
    """Entry point to demonstrate the sample status table."""
    comp_title = 'Sample status'
    sample_status = StatusTable(samples=["sample_1", "sample_2", "sample_3"])
    sample_status.set_status("sample_1", True, "Success")
    sample_status.set_status("sample_2", False, "Failed because of a reason")
    sample_status.add_column(
        col_name="var1",
        add_dict={"sample_1": 255, "sample_2": 315},
    )
    sample_status.add_badge_column(
        col_name="var2",
        statuses={
            "sample_1": True,
            "sample_2": False
        },
        messages={
            "sample_1": "Pass",
            "sample_2": "Fail"
        }
    )

    with sample_status:
        sample_status.write_table()
    report = ComponentReport(comp_title, sample_status)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'Sample status',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument(
        "--output",
        default="sample_status.html",
        help="Output HTML file."
    )
    return parser
