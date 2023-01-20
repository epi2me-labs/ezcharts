"""Get default cards layouts."""
from typing import Optional, Type
from uuid import uuid4

from dominate.tags import button, div, h5, html_tag

from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.util import cls


class IOffCanvasClasses(IClasses):
    """Cards html classes."""

    container: str = cls("container", "px-0")
    offcanvas: str = cls("offcanvas", "offcanvas-bottom", "h-auto")
    offcanvas_button: str = cls("btn")
    offcanvas_header: str = cls("offcanvas-header")
    offcanvas_title: str = cls("offcanvas-title")
    offcanvas_body: str = cls("offcanvas-body")


class OffCanvas(Snippet):
    """A styled section tag."""

    TAG = 'div'

    def __init__(
        self,
        title,
        label,
        body,
        classes: IOffCanvasClasses = IOffCanvasClasses(),
    ) -> None:
        """Create the layout."""
        super().__init__(
            styles=None,
            classes=classes,
            className=classes.container)

        with self:
            self.add_offcanvas(
                title,
                label,
                f"OffCanvas_{str(uuid4()).replace('-', '')}",
                body)

    def add_offcanvas(
        self,
        title: str,
        label: str,
        new_uid: str,
        body: Optional[str] = None,
        offcanvas_cls: Optional[str] = None,
        offcanvas_btn_cls: Optional[str] = "btn-primary",
        head_tag: Type[html_tag] = h5
    ) -> None:
        """Add cards to the grid."""
        button(
                label,
                type="button",
                data_bs_toggle="offcanvas",
                data_bs_target=f"#{new_uid}",
                aria_controls="offcanvasBottom",
                className=cls(
                    self.classes.offcanvas_button,
                    offcanvas_btn_cls if offcanvas_btn_cls is not None else '')
                )

        with div(
            id=new_uid,
            tabindex=-1,
            aria_labelledby="offcanvasBottomLabel",
            className=cls(
                self.classes.offcanvas,
                offcanvas_cls if offcanvas_cls is not None else '')):

            with div(className=cls(self.classes.offcanvas_header)):
                head_tag(title, className=self.classes.offcanvas_title)
                button(
                    type="button",
                    cls="btn-close",
                    data_bs_dismiss="offcanvas",
                    aria_label="Close")

            div(body, className=self.classes.offcanvas_body)
