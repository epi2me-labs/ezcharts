"""Get default tabs layouts."""
from dominate.tags import button, div, li, ul


class Tabs(div):
    """A styled div tag for creating tabbed layouts."""

    def __init__(
        self,
        container_classes: str = "justify-content-center",
        buttons_container_classes: str = "nav nav-pills py-3",
        content_container_classes: str = "tab-content"
    ) -> None:
        """Create tag."""
        super().__init__(
            tagname='div', className=container_classes)

        with self:
            self.buttons = ul(
                className=buttons_container_classes,
                id="pills-tab", role="tablist")
            self.contents = div(
                className=content_container_classes,
                id="pills-tabContent")

    def add_tab(self, title: str, active: bool) -> div:
        """Add a tab button and content container."""
        with self.buttons:
            self.tab_button(title, active)
        with self.contents:
            return self.tab_container(title, active)

    @staticmethod
    def tab_container(
        title: str,
        active: bool = False,
        container_classes: str = "tab-pane fade show"
    ) -> div:
        """
        Generate a tab content container.

        Compatible with Tabs.
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

    @staticmethod
    def tab_button(
        title: str,
        active: bool = False,
        list_item_classes: str = "nav-item",
        button_classes: str = "nav-link"
    ) -> None:
        """
        Generate a tab button.

        Compatible with Tabs.
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
