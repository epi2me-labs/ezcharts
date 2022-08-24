"""Get default stats layouts."""
from typing import List, Optional, Tuple, Type

from dominate.tags import div, h3, html_tag, p

from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.snippets import Grid
from ezcharts.layout.util import cls


class IStatsClasses(IClasses):
    """Stats html classes."""

    container: str = cls("container", "px-0", "mb-5")
    item: str = cls(
        "shadow-sm", "container", "p-4", "bg-white",
        "border", "rounded")
    item_heading: str = cls("h5", "mb-0", "pb-3")
    item_value: str = cls("fs-2", "mb-0")


class Stats(Snippet):
    """A styled section tag."""

    TAG = 'div'

    def __init__(
        self,
        columns: Optional[int] = 2,
        items: List[Tuple[str, str]] = [],
        classes: IStatsClasses = IStatsClasses(),
    ) -> None:
        """Create table."""
        super().__init__(
            styles=None,
            classes=classes,
            className=classes.container)

        with self:
            self.items = Grid(columns)

        with self.items:
            for item in items:
                self.add_stats_item(item[0], item[1])

    def add_stats_item(
        self,
        value: str,
        heading: str,
        heading_tag: Type[html_tag] = h3
    ) -> None:
        """Add a badge to the banner."""
        with self.items:
            with div(className=self.classes.item):
                heading_tag(
                    heading, className=self.classes.item_heading)
                p(value, className=self.classes.item_value)
