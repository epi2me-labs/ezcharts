"""Get default tabs layouts."""
from typing import Optional
import warnings

from dominate.tags import button, div, li, style, ul
from dominate.util import raw

from ezcharts.layout.base import IClasses, IStyles, Snippet
from ezcharts.layout.util import cls, css, render_template


warnings.simplefilter('always', DeprecationWarning)


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
        # store the number of tabs so that we know if a tab is the first one and should
        # be active
        self._ntabs: int = 0
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

    @property
    def _active_class_name(self) -> str:
        return "" if self._ntabs > 0 else " active"

    def add_tab(self, title: str, active: Optional[bool] = None) -> div:
        """Add a tab button and content container."""
        if active is not None:
            warnings.warn(
                "Explicitly passing 'active' parameter is deprecated "
                "and will be ignored.",
                DeprecationWarning, stacklevel=2)

        tab_id = f"{self.uid}-{self.get_uid('Tab')}"
        with self.buttons:
            with li(
                className=self.classes.tab_buttons_list_item,
                role="presentation"
            ):
                button(
                    title,
                    className=f"{self.classes.tab_button}{self._active_class_name}",
                    id=f"{tab_id}-tab",
                    type="button",
                    role="tab",
                    **self._get_button_data_aria(tab_id))

        with self.contents:
            return self._build_tab_container(tab_id)

    def add_dropdown_menu(
        self, title: str = "Dropdown", change_header: bool = True
    ) -> ul:
        """Get a dropdown menu."""
        button_id = f"{self.uid}-{self.get_uid('DropdownMenu')}"
        with self.buttons:
            with li(
                className=self.classes.tab_buttons_list_item + ' dropdown',
                role="presentation"
            ):
                button(
                    title,
                    className=f"{self.classes.tab_button} dropdown-toggle",
                    id=button_id,
                    href="#",
                    **{"data-bs-toggle": "dropdown"},
                    **({"data-ezc-updateDropDownTitle": ""} if change_header else {}))
                return ul(className="dropdown-menu")

    def add_dropdown_tab(
            self, title: str, active: Optional[bool] = None) -> div:
        """Get a dropdown tab."""
        if active is not None:
            warnings.warn(
                "Explicitly passing 'active' parameter is deprecated "
                "and will be ignored.",
                DeprecationWarning, stacklevel=2)

        tab_id = f"{self.uid}-{self.get_uid('DropdownItem')}"
        with li():
            button(
                title,
                className=f"dropdown-item{self._active_class_name}",
                id=f"#{tab_id}-tab",
                type="button",
                role="tab",
                **self._get_button_data_aria(tab_id))

        with self.contents:
            return self._build_tab_container(tab_id)

    def _build_tab_container(self, tab_id: str) -> div:
        """Get tab content container."""
        tab_container = div(
            className=f"{self.classes.tab_content}{self._active_class_name}",
            id=tab_id,
            role="tabpanel",
            **{"aria-labelledby": f"{tab_id}-tab"})
        # increment the number of tabs and return the div
        self._ntabs += 1
        return tab_container

    def _get_button_data_aria(self, tab_id: str) -> dict:
        """Get ARIA data for tab buttons."""
        return {
            "data-bs-toggle": "tab",
            "data-bs-target": f"#{tab_id}",
            "aria-controls": f"{tab_id}",
        }
