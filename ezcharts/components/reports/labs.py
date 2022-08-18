"""Get a default report."""
from datetime import datetime
from typing import List, Optional, Type

from dominate.tags import (
    a, code, div, h4, html_tag, li, nav, p, section, ul)

from ezcharts.components.params import ParamsTable
from ezcharts.components.reports import Report
from ezcharts.components.theme import (
    EPI2MELabsLogo, LAB_body_resources, LAB_head_resources)
from ezcharts.components.versions import version_table
from ezcharts.layout.resource import Resource
from ezcharts.layout.snippets.banner import Banner
from ezcharts.layout.snippets.section import Section


class LabsAddendum(div):
    """A styled footer component for use in a Report."""

    def __init__(
        self,
        workflow_name: str,
        footer_classes: str = "py-5 px-4 border-top",
        container_classes: str = "container px-0",
        use_defaults: bool = True
    ) -> None:
        """Create tag."""
        super().__init__(tagname='div', className=footer_classes)
        with self:
            self.container = div(className=container_classes)
        if use_defaults:
            with self.container:
                h4('About this report', className="pb-3")
                with p(
                    "This report was produced using the "
                    f"epi2me-labs/{workflow_name}. The workflow "
                    "can be run using"
                ):
                    code("nextflow epi2me-labs/wf-human-snp --help")
                p(
                    "Oxford Nanopore Technologies products are not "
                    "intended for use for health assessment or to "
                    "diagnose, treat, mitigate, cure or prevent any "
                    "disease or condition.")


class LabsNavigation(nav):
    """A styled nav component for use in a Report."""

    def __init__(
        self,
        logo: Type[html_tag],
        header_height: int = 75,
        header_classes: str = (
            "fixed-top d-flex align-items-center flex-wrap "
            "justify-content-center bg-dark"),
        container_classes: str = (
            "container px-0 d-flex flex-wrap "
            "justify-content-center align-items-center py-3"),
        logo_link_classes: str = (
            "d-flex align-items-center pe-5 mb-md-0 me-md-auto "
            "text-decoration-none"),
        list_class=(
            "nav nav-pills flex-row-reverse"),
    ) -> None:
        """Create tag."""
        spacer = div(
            className="d-flex",
            style=f"margin-top: {header_height}px;")
        super().__init__(
            tagname='nav', className=header_classes,
            style=f"min-height: {header_height}px;")
        spacer.add(self)
        with self:
            with div(className=container_classes):
                with a(href="/", className=logo_link_classes):
                    logo()
                self.links = ul(className=list_class, __pretty=False)

    def add_link(
        self,
        link_title: str,
        link_href: str,
        list_item_classes: str = "nav-item",
        list_item_link_classes: str = "nav-link text-white"
    ) -> None:
        """Add a header nav link to the header links list."""
        with self.links:
            with li(className=list_item_classes):
                a(link_title, href=link_href, className=list_item_link_classes)


class LabsReport(Report):
    """A basic report."""

    def __init__(
        self,
        report_title,
        workflow_name,
        workflow_params_path: str,
        workflow_versions_path: str,
        logo: Type[html_tag] = EPI2MELabsLogo,
        head_resources: List[Resource] = LAB_head_resources,
        body_resources: List[Resource] = LAB_body_resources,
        created_date: Optional[str] = None
    ) -> None:
        """Create tag."""
        super().__init__(
            report_title=report_title,
            head_resources=head_resources,
            body_resources=body_resources)

        with self.header:
            self.nav = LabsNavigation(logo=logo)
            self.nav.add_link('Parameters', '#workflow-parameters')
            self.nav.add_link('Versions', '#software-versions')

        with self.main:
            self.intro_content = section(id="intro-content", role="region")
            with self.intro_content:
                self.banner = Banner('Summary', report_title, workflow_name)
                self.banner.add_badge("Research use only")
                if not created_date:
                    created_date = datetime.today().strftime('%Y-%m-%d')
                self.banner.add_badge(created_date, bg_class="bg-secondary")

            self.main_content = section(id="main-content", role="region")

            self.meta_content = section(id="meta-content", role="region")
            with self.meta_content:
                with Section("software-versions", 'Software versions'):
                    version_table(workflow_versions_path)

                with Section("workflow-parameters", 'Workflow parameters'):
                    ParamsTable(workflow_params_path)

        with self.footer:
            self.addendum = LabsAddendum(workflow_name=workflow_name)

    def add_section(
        self,
        href: str,
        title: str,
        link_title: str
    ) -> Section:
        """Add a section to the main_content region."""
        self.nav.add_link(link_title, f'#{href}')
        with self.main_content:
            return Section(href, title)
