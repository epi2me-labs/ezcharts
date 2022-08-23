"""Get default section layouts."""
from typing import Optional, Type

from dominate.tags import h2, html_tag

from ezcharts.layout.base import BaseSnippet, IClasses, IStyles
from ezcharts.layout.util import cls


class ISectionClasses(IClasses):
    """Section html classes."""

    container: str = cls(
        "shadow-sm", "container", "p-4", "mb-5",
        "bg-white", "border", "rounded")
    title: str = cls("h5", "mb-0", "pb-3")


class ISectionStyles(IStyles):
    """Section inline css styles."""

    ...


class Section(BaseSnippet):
    """A styled section snippet."""

    TAG = "section"

    def __init__(
        self,
        section_id: str,
        section_title: Optional[str] = None,
        section_title_tag: Type[html_tag] = h2,
        styles: ISectionStyles = ISectionStyles(),
        classes: ISectionClasses = ISectionClasses()
    ) -> None:
        """Create styled section."""
        super().__init__(
            styles=styles,
            classes=classes,
            className=classes.container)

        if section_title and section_title_tag:
            with self:
                section_title_tag(
                    section_title,
                    className=self.classes.title)
