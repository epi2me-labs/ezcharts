"""Get default section layouts."""
from dominate.tags import section


def report_section(
    id: str,
    section_classes: str = "shadow container p-4 mb-5 bg-white rounded-3"
) -> section:
    """Generate a section with bootstrap styling by default."""
    return section(id=id, className=section_classes)
