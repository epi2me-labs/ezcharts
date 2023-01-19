"""Get a default report."""
from datetime import datetime
from typing import List, Optional, Type

from dominate.tags import (
    a, code, div, h4, html_tag, li, p, section, ul)

from ezcharts.components.params import ParamsTable
from ezcharts.components.reports import Report
from ezcharts.components.theme import (
    EPI2MELabsLogo, LAB_body_resources, LAB_head_resources)
from ezcharts.components.versions import VersionsTable
from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.resource import Resource
from ezcharts.layout.snippets.banner import Banner
from ezcharts.layout.snippets.section import Section
from ezcharts.layout.util import cls


class ILabsAddendumClasses(IClasses):
    """Section html classes."""

    container: str = cls("py-5", "px-4", "border-top")
    inner: str = cls("container", "px-0")


class LabsAddendum(Snippet):
    """A styled footer component for use in a Report."""

    TAG = 'div'

    def __init__(
        self,
        workflow_name: str,
        classes: ILabsAddendumClasses = ILabsAddendumClasses(),
        use_defaults: bool = True
    ) -> None:
        """Create tag."""
        super().__init__(
            styles=None,
            classes=classes,
            className=classes.container)

        with self:
            self.container = div(className=classes.inner)

        if use_defaults:
            with self.container:
                h4('About this report', className="pb-3")
                with p(
                    "This report was produced using the "
                    f"epi2me-labs/{workflow_name}. The workflow "
                    "can be run using"
                ):
                    code(f"nextflow epi2me-labs/{workflow_name} --help")
                p(
                    "Oxford Nanopore Technologies products are not "
                    "intended for use for health assessment or to "
                    "diagnose, treat, mitigate, cure or prevent any "
                    "disease or condition.")


class ILabsNavigationClasses(IClasses):
    """Section html classes."""

    spacer: str = cls("d-flex")
    container: str = cls(
        "fixed-top", "d-flex", "align-items-center", "flex-wrap",
        "justify-content-center", "bg-dark")
    inner: str = cls(
        "container", "px-0", "d-flex", "flex-wrap",
        "justify-content-center", "align-items-center", "py-3")
    logo: str = cls(
        "d-flex", "align-items-center", "pe-5", "mb-md-0",
        "me-md-auto", "text-decoration-none")
    nav_list: str = cls("nav", "nav-pills", "flex-row")
    nav_item: str = cls("nav-item")
    nav_item_link: str = cls("nav-link", "text-white")


class LabsNavigation(Snippet):
    """A styled nav component for use in a Report."""

    TAG = 'nav'

    def __init__(
        self,
        logo: Type[html_tag],
        groups: List[str],
        header_height: int = 75,
        classes: ILabsNavigationClasses = ILabsNavigationClasses()
    ) -> None:
        """Create tag."""
        spacer = div(
            className=classes.spacer,
            style=f"margin-top: {header_height}px;")

        super().__init__(
            styles=None,
            classes=classes,
            style=f"min-height: {header_height}px;",
            className=classes.container)

        spacer.add(self)
        with self:
            with div(className=self.classes.inner):
                with a(href="/", className=self.classes.logo):
                    logo()
                for group in groups:
                    setattr(
                        self, group,
                        ul(className=self.classes.nav_list, __pretty=False))

    def add_link(
        self,
        group: str,
        link_title: str,
        link_href: str
    ) -> None:
        """Add a header nav link to the header links list."""
        group_list = getattr(self, group)
        with group_list:
            with li(className=self.classes.nav_item):
                a(
                    link_title,
                    href=link_href,
                    className=self.classes.nav_item_link)


class BasicReport(Report):
    """A basic labs-themed report."""

    def __init__(
        self,
        report_title,
        logo: Type[html_tag] = EPI2MELabsLogo,
        head_resources: List[Resource] = LAB_head_resources,
        body_resources: List[Resource] = LAB_body_resources
    ) -> None:
        """Create tag."""
        super().__init__(
            report_title=report_title,
            head_resources=head_resources,
            body_resources=body_resources)
        with self.header:
            self.nav = LabsNavigation(logo=logo, groups=['main', 'meta'])

        with self.main:
            self.intro_content = section(id="intro-content", role="region")
            self.main_content = section(id="main-content", role="region")

    def add_section(
        self,
        title: str,
        link: str,
        overflow: bool = False
    ) -> Section:
        """Add a section to the main_content region."""
        href = link.lower().replace(' ', '_')
        self.nav.add_link('main', link, f'#{href}')
        with self.main_content:
            return Section(href, title, overflow=overflow)


class LabsReport(BasicReport):
    """A basic labs-themed report for a workflow."""

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
            self.nav.add_link('meta', 'Versions', '#versions')
            self.nav.add_link('meta', 'Parameters', '#parameters')
            self.intro_content = section(id="intro-content", role="region")
            with self.intro_content:
                self.banner = Banner(report_title, workflow_name)
                self.banner.add_badge("Research use only")
                if not created_date:
                    created_date = datetime.today().strftime('%Y-%m-%d')
                self.banner.add_badge(created_date, bg_class="bg-secondary")

        with self.main:
            self.meta_content = section(id="meta-content", role="region")
            with self.meta_content:
                with Section(
                    "versions",
                    'Software versions',
                    overflow=True
                ):
                    VersionsTable(workflow_versions_path)

                with Section(
                    "parameters",
                    'Workflow parameters',
                    overflow=True
                ):
                    ParamsTable(workflow_params_path)

        with self.footer:
            self.addendum = LabsAddendum(workflow_name=workflow_name)

    def add_badge(
        self,
        title: str,
        bg_class=None
    ) -> None:
        """Add a badge to the banner."""
        self.banner.add_badge(title, bg_class=bg_class)
