"""Get default tabs layouts."""
from dominate.tags import button, div, li, style, ul
from dominate.util import raw

from ezcharts.layout.base import IClasses, IStyles, Snippet
from ezcharts.layout.util import cls, css, render_template


class ITabsClasses(IClasses):
    """Tabs html classes."""

    container: str = cls("justify-content-center")
    tab_buttons_list: str = cls("nav", "nav-tabs", "mb-2")
    tab_buttons_list_item: str = cls("nav-item")
    tab_button: str = cls("nav-link", "px-0", "me-4", "text-muted")
    tab_contents_container: str = cls("tab-content", "p-5")
    tab_content: str = cls("tab-pane", "fade", "show")


class ITabsStyles(IStyles):
    """Tabs inline css styles."""

    tab_button: str = css(
        "margin-bottom: -1px",
        "font-weight: 600",
        "cursor: pointer",
        "border-color: transparent")
    tab_button_active: str = css(
        "border-bottom: 2px solid #0079a4",
        "color: #0079a4!important")


class Tabs(Snippet):
    """A styled div tag for creating tabbed layouts."""

    TAG = 'div'
    BUTTON_TEMPLATE = "#{{ id }}>ul>li>button { {{ styles }} };"
    BUTTON_TEMPLATE_ACTIVE = "#{{ id }}>ul>li>button.active { {{ astyles }} };"

    def __init__(
        self,
        styles: ITabsStyles = ITabsStyles(),
        classes: ITabsClasses = ITabsClasses()
    ) -> None:
        """Create tabs component."""
        super().__init__(
            styles=styles,
            classes=classes,
            className=classes.container)

        with self:
            style(raw(render_template(
                self.BUTTON_TEMPLATE,
                id=self.uid,
                styles=self.styles.tab_button)))
            style(raw(render_template(
                self.BUTTON_TEMPLATE_ACTIVE,
                id=self.uid,
                astyles=self.styles.tab_button_active)))
            self.buttons = ul(
                className=classes.tab_buttons_list,
                id="pills-tab",
                role="tablist")
            self.contents = div(
                className=classes.tab_contents_container,
                id="pills-tabContent")

    def add_tab(self, title: str, active: bool) -> div:
        """Add a tab button and content container."""
        _active = 'active' if active else ''
        lowered = title.lower()

        with self.buttons:
            with li(
                className=self.classes.tab_buttons_list_item,
                role="presentation"
            ):
                button(
                    title,
                    className=f"{self.classes.tab_button} {_active}",
                    id=f"{self.uid}-tabs-{lowered}-tab",
                    type="button",
                    role="tab",
                    **self._get_button_data_aria(lowered))

        with self.contents:
            return self._build_container(
                lowered, f"{self.classes.tab_content} {_active}")

    def add_dropdown_menu(self, title: str) -> ul:
        """Get a dropdown menu."""
        dropdown_link_data_aria = {"data-bs-toggle": "dropdown"}
        with self.buttons:
            with li(
                className=self.classes.tab_buttons_list_item + ' dropdown',
                role="presentation"
            ):
                button(
                    title,
                    className=f"{self.classes.tab_button} dropdown-toggle",
                    href="#",
                    **dropdown_link_data_aria)
                return ul(className="dropdown-menu")

    def add_dropdown_tab(self, title: str, active: bool) -> div:
        """Get a dropdown tab."""
        _active = 'active' if active else ''
        lowered = title.lower()

        with li():
            button(
                title,
                role="tab",
                className="dropdown-item",
                type="button",
                id=f"#{self.uid}-tabs-{lowered}-tab",
                **self._get_button_data_aria(lowered))

        with self.contents:
            return self._build_container(
                lowered, f"{self.classes.tab_content} {_active}")

    def _build_container(self, title: str, classes: str) -> div:
        """Get tab content container."""
        return div(
            className=classes,
            id=f"{self.uid}-tabs-{title}",
            role="tabpanel",
            **self._get_content_data_aria(title))

    def _get_button_data_aria(self, title: str):
        """Get ARIA data for tab buttons."""
        return {
            "data-bs-toggle": "tab",
            "data-bs-target": f"#{self.uid}-tabs-{title}",
            "aria-controls": f"{self.uid}-tabs-{title}",
        }

    def _get_content_data_aria(self, title: str):
        """Get ARIA data for tab content containers."""
        return {
            "aria-labelledby": f"{self.uid}-tabs-{title}-tab"
        }
