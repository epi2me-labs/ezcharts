"""Get default footer layouts."""
from typing import Callable, NamedTuple, Optional

from dominate.tags import code, div, footer, h4, p


def get_footer_defaults() -> None:
    """Generate default footer content."""
    h4('About this report', className="pb-3")
    with p(
        "This report was produced using the "
        "epi2me-labs/wf-human-snp. The workflow "
        "can be run using"
    ):
        code("nextflow epi2me-labs/wf-human-snp --help")
    p(
        "Oxford Nanopore Technologies products are not "
        "intended for use for health assessment or to "
        "diagnose, treat, mitigate, cure or prevent any "
        "disease or condition.")


class IFooterReturn(NamedTuple):
    """Specifies the return types for report_footer."""
    main: footer
    container: div


def report_footer(
    footer_classes: str = "py-5 px-4 border-top",
    container_classes: str = "container px-0",
    defaults_getter: Optional[Callable] = get_footer_defaults
) -> IFooterReturn:
    """
    Generate a footer component with labs-bootstrap
    styling by default and a div for containing content.

    :returns: The footer element and the div that
        contains the default content.
    """
    _footer = footer(className=footer_classes)
    with _footer:
        container = div(className=container_classes)
        if defaults_getter:
            with container:
                defaults_getter()    
        return IFooterReturn(_footer, container)
