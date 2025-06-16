"""Run ONT-specific ezCharts demo."""
import argparse

from ezcharts import util
from ezcharts.components.lead_summary import LeadSummary
from ezcharts.components.reports.ont import ONTReport


# Setup simple globals
WORKFLOW_NAME = 'wf-template'
WORKFLOW_VERSION = "v1.0.0"
REPORT_TITLE = f'{WORKFLOW_NAME}-report'


def main(args):
    """Demo for ONTReport functionality."""
    logger = util.get_named_logger("ezChartONTDemo")

    # Create ONTReport to demonstrate fonts and styles
    logger.info('Building ONT report')
    report = ONTReport(
        REPORT_TITLE,
        WORKFLOW_NAME,
        workflow_version=WORKFLOW_VERSION,
        default_content=True)

    with report.add_section("QC Status", 'QC Status'):
        LeadSummary(
            workflow_version=WORKFLOW_VERSION,
            sample_alias="demo_sample",
            reference="path/to/reference",
            qc_status={"status": True, "scope": "QC status"},
            qc_criteria=[
                {"status": True, "scope": "All acceptance criteria met"},
            ],
            other_data={"Basecaller": "basecaller model"},
        )

    output_filename = args.output
    logger.info(f'Writing ONT report to {output_filename}')
    report.write(output_filename)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        "ezcharts ont-demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--output", default="ezcharts_ont_demo_report.html",
        help="Output HTML file.")
    return parser
