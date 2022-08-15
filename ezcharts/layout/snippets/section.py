"""Get default section layouts."""
from typing import Optional, Type

from dominate.tags import h2, html_tag


class Section(html_tag):
    """A styled section tag."""

    def __init__(
        self,
        section_id: str,
        section_title: Optional[str] = None,
        section_title_tag: Type[html_tag] = h2,
        section_classes: str = "shadow container p-4 mb-5 bg-white rounded-3"
    ) -> None:
        """Create tag."""
        super().__init__(
            tagname='section', id=section_id, className=section_classes)

        if section_title and section_title_tag:
            with self:
                section_title_tag(section_title)
