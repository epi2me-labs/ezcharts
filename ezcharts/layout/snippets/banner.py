"""Get default summary bar layouts."""
from dominate.tags import div, h1, p

from ezcharts.layout.base import IClasses, IStyles, Snippet
from ezcharts.layout.util import cls, css


class IBadgeClasses(IClasses):
    """Section html classes."""

    container: str = cls(
        "badge", "px-3", "py-2", "mb-3", "me-3", "badge")
    container_bg: str = cls("bg-primary")


class IBadgeStyles(IStyles):
    """Section inline css styles."""

    container: str = css(
        "line-height: 20px", "border-radius: 6px",
        "font-size: 13px;")


class Badge(Snippet):
    """A styled span."""

    TAG = 'span'

    def __init__(
        self,
        title: str,
        bg_class=None,
        styles: IBadgeStyles = IBadgeStyles(),
        classes: IBadgeClasses = IBadgeClasses(),
    ) -> None:
        """Create styled badge."""
        bg = bg_class or classes.container_bg
        super().__init__(
            title,
            styles=styles,
            classes=classes,
            className=f"{classes.container} {bg}",
            style=styles.container)


class IBannerClasses(IClasses):
    """Section html classes."""

    container: str = cls("px-4", "bg-dark")
    inner: str = cls("container", "px-0", "py-5", "border-top", "text-white")


class IBannerStyles(IStyles):
    """Section inline css styles."""

    container: str = css(
        "margin-bottom: -25px",
        "padding-bottom: 35px !important")
    inner: str = css("border-color: rgba(255, 255, 255, 0.1) !important;")


class Banner(Snippet):
    """A styled div tag containing a heading and badges."""

    TAG = 'div'

    def __init__(
        self,
        report_title: str,
        workflow_name: str,
        styles: IBannerStyles = IBannerStyles(),
        classes: IBannerClasses = IBannerClasses(),
        default_content: bool = True
    ) -> None:
        """Create styled banner."""
        super().__init__(
            styles=styles,
            classes=classes,
            className=classes.container,
            style=styles.container)

        with self:
            with div(className=classes.inner, style=styles.inner):
                if not default_content:
                    return
                h1(report_title)
                p(
                    f"Results generated through the {workflow_name} nextflow "
                    "workflow provided by Oxford Nanopore Technologies.",
                    className="py-3 fs-5")
                self.badges = div(className="d-flex flex-wrap")

    def add_badge(
        self,
        title: str,
        bg_class=None,
        styles: IBadgeStyles = IBadgeStyles(),
        classes: IBadgeClasses = IBadgeClasses(),
    ) -> None:
        """Add a badge to the banner."""
        with self.badges:
            Badge(title, styles=styles, classes=classes, bg_class=bg_class)
