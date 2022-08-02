"""Get default tabs layouts."""
from typing import NamedTuple

from dominate.tags import button, div, li, ul


def report_tab_button(
    title: str,
    active: bool = False,
    list_item_classes: str = "nav-item",
    button_classes: str = "nav-link"
) -> None:
    """
    Generate a tab buttons list item, compatible with
    report_tabs.
    """
    _active = 'active' if active else ''
    lowered = title.lower()
    tab_button_data_aria = {
        "data-bs-toggle": "pill",
        "data-bs-target": f"#pills-{lowered}",
        "aria-controls": f"pills-{lowered}",
        "aria-selected": "true"
    }
    with li(className=list_item_classes, role="presentation"):
        button(
            title,
            className=f"{button_classes} {_active}",
            id=f"pills-{lowered}-tab",
            type="button",
            role="tab",
            **tab_button_data_aria)


def report_tab_container(
    title: str,
    active: bool = False,
    container_classes: str = "tab-pane fade show"
) -> div:
    """
    Generate a tab content container, compatible with
    report_tabs.
    """
    _active = 'active' if active else ''
    lowered = title.lower()
    tab_content_data_aria = {
        "aria-labelledby": f"pills-{lowered}-tab"
    }
    return div(
        className=f"{container_classes} {_active}",
        id=f"pills-{lowered}",
        role="tabpanel",
        **tab_content_data_aria)


class ITabsReturn(NamedTuple):
    """Specifies the return types for report_tabs."""
    main: div
    buttons: ul
    containers: div


def report_tabs(
    container_classes: str = "justify-content-center",
    buttons_container_classes: str = "nav nav-pills py-3",
    content_container_classes: str = "tab-content"
) -> ITabsReturn:
    """
    Generate a tabs component with labs-bootstrap
    styling by default. Headers can provided via the
    so-named argument. Rows can provided by nesting under
    the returned body attribute, as per usual.

    :returns: The wrapping div element and the buttons
        and content container elements.
    """
    _tabs = div(className=container_classes)
    with _tabs:
        tabs_list = ul(
            className=buttons_container_classes,
            id="pills-tab", role="tablist")
        tabs_content = div(
            className=content_container_classes,
            id="pills-tabContent")
    return ITabsReturn(_tabs, tabs_list, tabs_content)
