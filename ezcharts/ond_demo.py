"""Run OND-specific ezCharts demo."""
import argparse

from ezcharts import util
from ezcharts.components.lead_summary import LeadSummary
from ezcharts.components.reports.ond import ONDReport


# Setup simple globals
WORKFLOW_NAME = 'wf-template'
WORKFLOW_VERSION = "v1.0.0"
REPORT_TITLE = f'{WORKFLOW_NAME}-report'


def main(args):
    """Demo for ONDReport functionality."""
    logger = util.get_named_logger("ezChartONDDemo")

    # Create ONDReport to demonstrate fonts and styles
    logger.info('Building OND report')
    report = ONDReport(
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
    logger.info(f'Writing OND report to {output_filename}')
    report.write(output_filename)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        "ezcharts ond-demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--output", default="ezcharts_ond_demo_report.html",
        help="Output HTML file.")
    return parser
