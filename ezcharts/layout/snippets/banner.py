"""Get default summary bar layouts."""
from dominate.tags import div, h1, html_tag, p


class Banner(html_tag):
    """A styled div tag containing a heading and badges."""

    def __init__(
        self,
        banner_id: str,
        report_title: str,
        workflow_name: str,
        summary_classes: str = "py-5 px-4 mb-5 border-bottom",
        container_classes: str = "container px-0"
    ) -> None:
        """Create tag."""
        super().__init__(
            tagname='div', id=banner_id, className=summary_classes)
        with self:
            with div(className=container_classes):
                h1(report_title)
                p(
                    f"Results generated through the {workflow_name} nextflow "
                    "workflow provided by Oxford Nanopore Technologies.",
                    className="py-3")
                self.badges = div(className="d-flex flex-wrap")

    def add_badge(
        self,
        title: str,
        bg_class: str = "bg-dark"
    ) -> None:
        """Add a badge to the banner."""
        with self.badges:
            Badge(title, bg_colour_class=bg_class)


class Badge(html_tag):
    """A styled span."""

    def __init__(
        self,
        title: str,
        badge_classes: str = "badge px-4 py-2 mb-3 me-3 badge",
        bg_colour_class: str = "bg-dark"
    ) -> None:
        """Create tag."""
        super().__init__(
            title,
            tagname='span',
            className=f"{badge_classes} {bg_colour_class}")
