"""Re-usable report components."""
from typing import List, Type

from dominate.tags import body, footer, head, header, main, title

from ezcharts.layout.base import Snippet
from ezcharts.layout.resource import (
    base_body_resources, base_head_resources, Resource)
from ezcharts.layout.snippets.document import DefaultBody, DefaultHead
from ezcharts.layout.util import write_report


class Report(Snippet):
    """A basic report."""

    TAG: str = 'html'

    def __init__(
        self,
        report_title,
        head_tag: Type[head] = DefaultHead,
        body_tag: Type[body] = DefaultBody,
        head_resources: List[Resource] = base_head_resources,
        body_resources: List[Resource] = base_body_resources
    ) -> None:
        """Create tag."""
        super().__init__(
            styles=None,
            classes=None)

        with self:
            # Adds the generic meta tags for us!
            self.head = head_tag()
            # Enables scroll spy globals for us!
            self.body = body_tag()

        with self.head:
            title(report_title)
            for resource in head_resources:
                resource()

        with self.body:
            self.header = header()
            self.main = main()
            self.footer = footer()
            for resource in body_resources:
                resource()

    def write(self, path):
        """Write a report to file."""
        write_report(path, self)
