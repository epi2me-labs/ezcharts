"""A reusable lead table."""

from datetime import datetime
import math

from dominate.tags import (
    div, li, span, strong,
    table, td, th, thead, tr, ul
)  # noqa: F401

from ezcharts.layout.base import Snippet


class LeadSummary(Snippet):
    """Display lead table and QC summary box."""

    def __init__(
        self,
        workflow_version,
        sample_alias,
        client_fields=None,
        reference=None,
        qc_status=None,
        qc_criteria=None,
        other_data=None,
        margin_bottom=3,
        **kwargs,
    ) -> None:
        """Create LeadSummary component.

        :param workflow_version: Workflow version.
        :param sample_alias: Sample alias.
        :param client_fields: Client fields dictionary.
        :param reference: Reference ID.
        :param qc_status: Dict of the QC status of the sample.
        :param qc_criteria: List of dict of the QC criteria summary to be reported.
        :param other_data: Dict of tuples to be added to the leadsection table.

        """
        super().__init__(styles=None, classes=None)

        lead_fields = {
            "Sample": sample_alias,
            "Workflow version": workflow_version,
            "Report generated on": str(datetime.now()),
            "Reference": reference,
        }
        # Update the dict with extra data to be included
        if other_data:
            lead_fields.update(other_data)

        lead_summary = lead_section_table(
            lead_fields,
            client_fields=client_fields,
            margin_bottom=margin_bottom,
            **kwargs
        )

        with div(cls="row"):
            div(lead_summary, cls="col-sm-8")

            with div(cls="col-sm-4"):
                # Define common style
                _ul = ul(cls="list-group")
                li_classes = ["list-group-item", "mb-0"]
                # Add QC status
                qc_li_classes = li_classes.copy()
                qc_li_classes.extend(["h4", "pt-3", "pb-3"])
                if not qc_status or not qc_criteria:
                    pass
                elif "status" not in qc_status:
                    raise Exception("No status found in the QC status dictionary")
                else:
                    qc_span = make_badge(qc_status["status"], fill_background=False)
                    qc_li_classes.append(
                        "list-lead-pass" if qc_status["status"] else "list-lead-fail"
                    )
                    qc_li = li(qc_status["scope"], qc_span, cls=" ".join(qc_li_classes))
                    _ul.add(qc_li)
                    # For individuals QC criteria
                    qc_criteria_li_classes = li_classes.copy()
                    qc_criteria_li_classes.extend(["pt-2", "pb-2"])
                    for qc_item in qc_criteria:
                        criteria_span = make_badge(
                            qc_item["status"], fill_background=True
                        )

                        criteria_li = li(
                            qc_item["scope"],
                            criteria_span,
                            cls=" ".join(qc_criteria_li_classes),
                        )
                        _ul.add(criteria_li)


# Used within lead_summary but also on its own
def lead_section_table(
    lead_fields,
    client_fields=None,
    margin_bottom=3,
    n_columns=2,
):
    """From a dict of key value pairs make a table leading section.

    :param lead_fields: Dictionary of title:value pairs.
    :param client_fields: Client fields dictionary.
    :param margin_bottom: bottom margin.
    :param n_columns: Number of columns to display.

    """
    error = None

    table_cls = f"table table-sm small mb-{margin_bottom}"

    if not client_fields:
        pass  # no additional fields to worry about
    elif "error" in client_fields:
        error = div(
            f"ERROR: {client_fields['error']}",
            cls="alert alert-danger",
        )
    else:
        lead_fields.update(client_fields)

    _row = div(cls="row")
    _div = div(cls="col m-6")
    _table = table(cls=table_cls)
    if error:
        _div.add(error)
    # Create one table per column. We calculate in advance the max number
    # of rows per table.
    n_fields = len(lead_fields)
    # Determine rows per column
    column_row_limit = math.ceil(n_fields / n_columns)

    count = 0

    for key, value in lead_fields.items():
        if count == column_row_limit:
            _row.add(_div)
            _div = div(cls="col m-6")
            count = 0
        # Check for None, too as client fields reformats fields to this
        if value is None:
            continue
        _table.add(
            tr(td(strong(key)), td(value))
        )

        count += 1

        if count == column_row_limit:
            _div.add(_table)
            _table = table(cls=table_cls)
    _div.add(_table)
    _row.add(_div)
    return _row


class WorkflowQCBanner(Snippet):
    """Display Quality Control banner in PDF report."""

    def __init__(
        self,
        workflow_pass,
        fill_background=False,  # switch between 'solid' or ''
        **kwargs,
    ) -> None:
        """Create LeadSummary component.

        :param workflow_pass: Boolean with the resulting validation of the workflow.
        :param fill_background: Boolean for background color (true).

        """
        super().__init__(styles=None, classes=None)

        if workflow_pass:
            alert_class = "success"
        else:
            alert_class = "danger"

        with div("Quality control status", cls=f"alert alert-{alert_class}"):
            make_badge(workflow_pass, fill_background=fill_background)


def make_badge(status, fill_background=True):
    """Make a status badge."""
    badge_classes = ["badge", "rounded-pill", "p-2", "mr-2", "float-end"]
    if fill_background:
        fill_background_conversion = "-solid"
    else:
        fill_background_conversion = ""
    if status:
        badge_classes.append(f"badge-icon badge-pass{fill_background_conversion}")
        msg = "Pass"
    else:
        badge_classes.append(f"badge-icon badge-fail{fill_background_conversion}")
        msg = "Fail"

    return span(msg, cls=" ".join(badge_classes))


def make_table():
    """Create structure for PDF reports individual checks table."""
    _table = table(cls="table table-sm small mb-4")
    _table.add(
        thead(
            th("Check name"),
            th("Value"),
            th("Acceptance Criteria"),
            th("Status")
        )
    )
    return _table
