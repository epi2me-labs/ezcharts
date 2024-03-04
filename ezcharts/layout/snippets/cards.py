"""Get default cards layouts."""
from typing import List, NamedTuple, Optional, Type

from dominate.tags import (
    div, h5, html_tag, p, span, strong, table, td, tr)

from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.snippets import Grid
from ezcharts.layout.snippets import OffCanvas
from ezcharts.layout.util import cls


class ICard(NamedTuple):
    """Card definition class."""

    body: object
    head: Optional[str] = None
    alias: Optional[str] = None
    barcode: Optional[str] = None
    status: Optional[str] = None
    head_msg: Optional[str] = None
    footer: Optional[str] = None
    classes: Optional[str] = None
    offcanvas_params: Optional[dict] = None


class ICardClasses(IClasses):
    """Cards html classes."""

    container: str = cls("container", "px-0")
    card: str = cls("card", "px-0", "mb-4", "shadow-sm")
    card_body: str = cls("card-body")
    card_heading: str = cls("card-header")
    card_text: str = cls("card-text")
    card_footer: str = cls("card-footer small")


class Cards(Snippet):
    """A styled section tag."""

    TAG = 'div'

    def __init__(
        self,
        columns: Optional[int] = 2,
        items: List[ICard] = [],
        classes: ICardClasses = ICardClasses(),
    ) -> None:
        """Create the grid layout."""
        super().__init__(
            styles=None,
            classes=classes,
            className=classes.container)

        with self:
            self.items = Grid(columns)

        with self.items:
            for item in items:
                self.add_card(
                    item.body,
                    item.head,
                    item.alias,
                    item.barcode,
                    item.status,
                    item.footer,
                    item.classes,
                    item.offcanvas_params
                    )

    def add_card(
        self,
        body: object,
        head: Optional[str] = None,
        alias: Optional[str] = None,
        barcode: Optional[str] = None,
        status: Optional[str] = None,
        footer: Optional[str] = None,
        card_cls: Optional[str] = None,
        offcanvas_params: Optional[dict] = None,
        head_tag: Type[html_tag] = h5,
        body_tag: Type[html_tag] = p

    ) -> None:
        """Add cards to the grid."""
        with self.items:
            with div(
                    className=cls(
                        self.classes.card,
                        card_cls if card_cls is not None else '')):

                # sample badge
                if status:
                    sample_badge_cls = [
                        'badge', 'badge-icon-solid', 'rounded-pill', 'p-2']
                    if status == 'pass':
                        sample_badge_cls.append('badge-pass-solid')
                        msg = "Pass"
                    elif status == 'warn':
                        sample_badge_cls.append('badge-unknown-solid')
                        msg = "Warning"
                    elif status == 'fail':
                        sample_badge_cls.append('badge-fail-solid')
                        msg = "Fail"
                    else:
                        msg = status
                    _span = span(msg, cls=' '.join(sample_badge_cls))

                # rest of heading
                with div(className=self.classes.card_heading):
                    if head:
                        head_tag(head)
                    else:
                        with div(className="row"):
                            with div(className="col-md-3"):
                                with table():
                                    with tr(cls="col-md-3"):
                                        if alias:
                                            td(strong(alias), cls="pr-4")
                                        if barcode:
                                            td(barcode, cls="px-4")
                                        if status:
                                            td(_span)
                            if offcanvas_params is not None:
                                with div(className="col-md-9"):
                                    OffCanvas(**offcanvas_params).render()

                # add body
                with div(className=self.classes.card_body):
                    try:
                        body_tag(body, className=self.classes.card_text)
                    except TypeError:
                        body_tag(body)

                # add footer if needed
                if footer is not None:
                    div(footer, className=self.classes.card_footer)
