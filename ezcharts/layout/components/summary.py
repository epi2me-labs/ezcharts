"""Get default summary bar layouts."""
from typing import NamedTuple

from dominate.tags import div, h1, p, section, span


def report_summary_badge(
    badge_title: str,
    badge_classes: str = "badge px-4 py-2 mb-3 me-3 badge",
    bg_colour_class: str = "bg-dark"
) -> span:
    """Generate a report_summary compatible badge with
    labs-bootstrap styling."""
    return span(
        badge_title,
        className=f"{badge_classes} {bg_colour_class}")


class ISummaryReturn(NamedTuple):
    """Specifies the return types for report_summary."""
    main: section
    badges: div


def report_summary(
    id: str,
    report_title: str,
    workflow_name: str
) -> ISummaryReturn:
    """
    Generate a section housing a report title and a container
    for badges containing meta information with labs-bootstrap
    styling by default.

    :returns: The section element and the div that
        contains the badges.
    """
    _summary = section(id=id, className="py-5 px-4 mb-5 border-bottom")
    with _summary:
        with div(className="container px-0"):
            h1(report_title)
            p(f"Results generated through the {workflow_name} nextflow "
              "workflow provided by Oxford Nanopore Technologies.",
              className="py-3")
            _badges = div(className="d-flex flex-wrap")
    return ISummaryReturn(_summary, _badges)
