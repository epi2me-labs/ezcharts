"""Get a default report."""
from typing import List, Type

from dominate.tags import (
    a, button, code, div, h4, html_tag, p, section)

from ezcharts.components.reports import Report
from ezcharts.components.theme import (
    ONT_body_resources, ONT_head_resources, ONTLogo)
from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.resource import Resource
from ezcharts.layout.snippets.banner import Banner
from ezcharts.layout.snippets.section import Section
from ezcharts.layout.util import cls


class ILabsAddendumClasses(IClasses):
    """Section html classes."""

    container: str = cls("py-5", "px-4")
    inner: str = cls("container", "px-0")


class LabsAddendum(Snippet):
    """A styled footer component for use in a Report."""

    TAG = 'div'

    def __init__(
        self,
        workflow_name: str,
        workflow_version: str,
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
                p(
                    "This report was produced using the ",
                    code(f"epi2me-labs/{workflow_name}"),
                    f" workflow ({workflow_version})."
                )
                p(
                    "Oxford Nanopore Technologies products are not "
                    "intended for use for health assessment or to "
                    "diagnose, treat, mitigate, cure or prevent any "
                    "disease or cONTition.")


class ILabsNavigationClasses(IClasses):
    """Section html classes."""

    spacer: str = cls("d-flex")
    container: str = cls(
        "fixed-top", "d-flex", "align-items-center", "flex-wrap",
        "justify-content-center", "bg-dark")
    inner: str = cls(
        "container", "px-0", "d-flex", "flex-wrap", "py-2")
    logo: str = cls(
        "d-flex", "align-items-center", "pe-5", "mb-md-0",
        "me-md-auto", "text-decoration-none")
    dropdown_btn: str = cls("btn", "btn-dark", "dropdown-toggle")
    dropdown_menu: str = cls("dropdown-menu")
    dropdown_item_link: str = cls("dropdown-item")


class LabsNavigation(Snippet):
    """A styled nav component for use in a Report."""

    TAG = 'nav'

    def __init__(
        self,
        logo: Type[html_tag],
        groups: List[str],
        header_height: int = 75,
        classes: ILabsNavigationClasses = ILabsNavigationClasses(),
        to_print: bool = False
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

                if not to_print:
                    button(
                        "Jump to section... ",
                        cls=self.classes.dropdown_btn,
                        type="button",
                        id="dropdownMenuButton",
                        data_bs_toggle="dropdown",
                        aria_haspopup="true",
                        aria_expanded="false")

                ngroups = len(groups)
                with div(className=self.classes.dropdown_menu):
                    for count, group in enumerate(groups):
                        setattr(
                            self, group,
                            div(className='', __pretty=False))
                        if count != ngroups - 1:
                            div(cls="dropdown-divider")

    def add_link(
        self,
        group: str,
        link_title: str,
        link_href: str
    ) -> None:
        """Add a header nav link to the header links list."""
        group_list = getattr(self, group)
        with group_list:
            a(
                link_title,
                href=link_href,
                className=self.classes.dropdown_item_link)


class BasicReport(Report):
    """A basic labs-themed report."""

    def __init__(
        self,
        report_title,
        logo: Type[html_tag] = ONTLogo,
        head_resources: List[Resource] = ONT_head_resources,
        body_resources: List[Resource] = ONT_body_resources,
        to_print: bool = False
    ) -> None:
        """Create tag."""
        super().__init__(
            report_title=report_title,
            head_resources=head_resources,
            body_resources=body_resources)

        with self.header:
            self.nav = LabsNavigation(
                logo=logo, groups=['main', 'meta'], to_print=to_print)

        with self.main:
            self.intro_content = section(id="intro-content", role="region")
            self.main_content = section(id="main-content", role="region")

    def add_section(
        self,
        title: str,
        link: str,
        overflow: bool = False,
        display_link: bool = True,
        transparent: bool = False,
    ) -> Section:
        """Add a section to the main_content region."""
        href = link.lower().replace(' ', '_')
        if display_link is True:
            self.nav.add_link('main', link, f'#{href}')

        with self.main_content:
            return Section(href, title, overflow=overflow, transparent=transparent)


class ONTReport(BasicReport):
    """A basic labs-themed report for a workflow."""

    def __init__(
        self,
        report_title,
        workflow_name,
        workflow_version: str,
        logo: Type[html_tag] = ONTLogo,
        head_resources: List[Resource] = ONT_head_resources,
        body_resources: List[Resource] = ONT_body_resources,
        default_content: bool = True,
        to_print: bool = False
    ) -> None:
        """Create tag."""
        super().__init__(
            report_title=report_title,
            head_resources=head_resources,
            body_resources=body_resources,
            to_print=to_print)

        if default_content is True:
            with self.header:
                self.intro_content = section(id="intro-content", role="region")
                with self.intro_content:
                    self.banner = Banner(report_title, workflow_name, subtitle=False)
                    self.banner.add_badge("Research use only", bg_class='bg-secondary')
                    self.banner.add_badge(workflow_version)

    def add_badge(
        self,
        title: str,
        bg_class=None
    ) -> None:
        """Add a badge to the banner."""
        self.banner.add_badge(title, bg_class=bg_class)
