"""Get a default report."""
from typing import List, Type

from dominate.tags import a, div, h4, html_tag, p

from ezcharts.components.ezchart import EZChart
from ezcharts.components.reports import Report
from ezcharts.components.theme import (
    EPI2MELabsLogo, LAB_body_resources, LAB_head_resources)
from ezcharts.layout.resource import Resource
from ezcharts.layout.snippets.section import Section


class ComponentReport(Report):
    """A report for displaying a component."""

    headerbar_classes: str = (
        "d-flex align-items-center flex-wrap "
        "justify-content-center bg-dark mb-5")
    headerbar_content_classes: str = (
        "container px-0 d-flex flex-wrap "
        "justify-content-center align-items-center py-3")
    logo_link_classes: str = (
        "d-flex align-items-center pe-5 mb-md-0 me-md-auto "
        "text-decoration-none")
    addendum_classes: str = "py-5 px-4 border-top"
    addendum_content_classes: str = "container px-0"

    def __init__(
        self,
        component_title: str,
        component_element: html_tag,
        logo: Type[html_tag] = EPI2MELabsLogo,
        head_resources: List[Resource] = LAB_head_resources,
        body_resources: List[Resource] = LAB_body_resources,
    ) -> None:
        """Create tag."""
        super().__init__(
            report_title=component_title,
            head_resources=head_resources,
            body_resources=body_resources)

        with self.header:
            with div(className=self.headerbar_classes):
                with div(className=self.headerbar_content_classes):
                    with a(href="/", className=self.logo_link_classes):
                        logo()

        with self.main:
            comp_container = Section('component', component_title)
            comp_container.add(component_element)

        with self.footer:
            with div(className=self.addendum_classes):
                with div(className=self.addendum_content_classes):
                    h4('About this report', className="pb-3")
                    p(
                        "This report was produced using the "
                        f"{component_title} component from ezcharts, "
                        "which is re-usable in other reports."
                    )
                    p(
                        "Oxford Nanopore Technologies products are not "
                        "intended for use for health assessment or to "
                        "diagnose, treat, mitigate, cure or prevent any "
                        "disease or condition.")

    @staticmethod
    def from_plot(plot, path, title="ezChart plot", **kwargs):
        """Create component report from a plot.

        :params path: path to output file.
        :param kwargs: passed to `EZChart`.
        """
        chart = EZChart(plot, "epi2melabs", **kwargs)
        report = ComponentReport(title, chart)
        report.write(path)
