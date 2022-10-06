"""Get default cards layouts."""
from typing import List, NamedTuple, Optional, Type

from dominate.tags import div, h5, html_tag, p

from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.snippets import Grid
from ezcharts.layout.util import cls


class ICard(NamedTuple):
    """Card definition class."""

    head: str
    body: str
    footer: Optional[str] = None
    classes: Optional[str] = None


class ICardClasses(IClasses):
    """Cards html classes."""

    container: str = cls("container", "px-0")
    card: str = cls("card", "px-0", "mb-4")
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
                self.add_card(item.head, item.body, item.footer, item.classes)

    def add_card(
        self,
        head: str,
        body: str,
        footer: Optional[str] = None,
        card_cls: Optional[str] = None,
        head_tag: Type[html_tag] = h5,
        body_tag: Type[html_tag] = p
    ) -> None:
        """Add cards to the grid."""
        with self.items:
            with div(
                    className=cls(
                        self.classes.card,
                        card_cls if card_cls is not None else '')):
                head_tag(head, className=self.classes.card_heading)
                with div(className=self.classes.card_body):
                    body_tag(body, className=self.classes.card_text)
                if footer is not None:
                    div(footer, className=self.classes.card_footer)
