"""Get a default report."""
from datetime import datetime
from typing import Optional, Type

from dominate.tags import (
    a, code, div, footer, h4, header, html, html_tag, li, main, p, ul)

from ezcharts.layout.resources import EPI2ME_labs_theme, Theme
from ezcharts.layout.snippets.banner import Banner
from ezcharts.layout.snippets.document import DefaultBody, DefaultHead
from ezcharts.layout.snippets.section import Section
from ezcharts.layout.snippets.table import params_table, version_table


class SimpleReportFooter(footer):
    """A styled footer component for use in a Report."""

    def __init__(
        self,
        workflow_name: str,
        footer_classes: str = "py-5 px-4 border-top",
        container_classes: str = "container px-0",
        use_defaults: bool = True
    ) -> None:
        """Create tag."""
        super().__init__(tagname='footer', className=footer_classes)
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


class SimpleReportHeader(header):
    """A styled header component for use in a Report."""

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
            tagname='header', className=header_classes,
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


class SimpleReport(html):
    """A basic report."""

    def __init__(
        self,
        report_title,
        workflow_name,
        workflow_params_path: str,
        workflow_versions_path: str,
        theme: Theme = EPI2ME_labs_theme,
        created_date: Optional[str] = None,
    ) -> None:
        """Create tag."""
        if not created_date:
            created_date = datetime.today().strftime('%Y-%m-%d')

        super().__init__(tagname='html')
        with self:
            # Adds the generic meta tags for us!
            self.head = DefaultHead(doc_title=report_title)
            # Enables scroll spy globals for us!
            self.body = DefaultBody()

        with self.head:
            # Head resources
            theme.render_head_resources()

        with self.body:
            self.header = SimpleReportHeader(logo=theme.logo)
            self.header.add_link('Parameters', '#workflow-parameters')
            self.header.add_link('Versions', '#software-versions')

            self.banner = Banner('Summary', report_title, workflow_name)
            self.banner.add_badge("Research use only")
            self.banner.add_badge(created_date, bg_class="bg-secondary")

            self.main = main()

            with Section("software-versions", 'Software versions'):
                version_table(workflow_versions_path)

            with Section("workflow-parameters", 'Workflow parameters'):
                params_table(workflow_params_path)

            SimpleReportFooter(workflow_name)

            # Post-load resources
            theme.render_body_resources()
