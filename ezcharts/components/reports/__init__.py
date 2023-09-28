"""Re-usable report components."""
from typing import List, Type

from bokeh.embed import components
from dominate.tags import body, footer, head, header, main, style, title
from dominate.util import raw

from ezcharts.components.ezchart import _BokehChart
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
        # check if the report contains `Bokeh` plots
        bokeh_charts = self.get_bokeh_charts()
        if bokeh_charts:
            # get the script + divs for all the plots; then place the div in the
            # corresponding `_BokehChart` div
            bokeh_script, bokeh_divs = components([x.plot._fig for x in bokeh_charts])
            for chart, bokeh_div in zip(bokeh_charts, bokeh_divs):
                with chart:
                    raw(bokeh_div)
            # add the script to the header
            with self.head:
                # make sure the plots fill out the enclosing div
                style(
                    """
                    .bk-Figure {
                        height: 100%;
                        width: 100%;
                    }
                    """
                )
                raw(bokeh_script)

        write_report(path, self)

    def get_bokeh_charts(self):
        """Return all children of the report that are of type `_BokehChart`."""
        bokeh_charts = []

        def _get_charts_in_children(s):
            if not hasattr(s, 'children') or not s.children:
                return
            for child in s.children:
                if isinstance(child, _BokehChart):
                    bokeh_charts.append(child)
                _get_charts_in_children(child)

        _get_charts_in_children(self)
        return bokeh_charts
