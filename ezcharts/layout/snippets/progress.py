"""Get default cards layouts."""
from typing import Optional

from dominate.tags import div, span

from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.util import cls


class IProgressClasses(IClasses):
    """Progress html classes."""

    container: str = None
    progress: str = cls("progress align-items-center position-relative")
    progress_bar: str = cls("progress-bar")


class Progress(Snippet):
    """A styled section tag."""

    TAG = 'div'

    def __init__(
        self,
        value_min: int = 0,
        value_max: int = 100,
        value_now: int = 50,
        display_val: Optional[str] = None,
        bar_cls: Optional[str] = None,
        height: Optional[int] = None,
        title: Optional[str] = None,
        styles: Optional[str] = None,
        classes: IProgressClasses = IProgressClasses()
    ) -> None:
        """Create the layout."""
        super().__init__(
            styles=None,
            classes=classes,
            className=classes.container)

        with self:
            self.add_progress(
                value_min,
                value_max,
                value_now,
                display_val,
                bar_cls,
                title,
                height)

    def add_progress(
        self,
        value_min: int,
        value_max: int,
        value_now: int,
        display_val: Optional[str] = None,
        bar_cls: Optional[str] = None,
        title: Optional[str] = None,
        height: Optional[int] = None
    ) -> None:
        """Add progress bar to the layout."""
        # Add a title of one is defined
        span(title, className=cls("fw-bold")) if title is not None else ''

        # Set style if height of bar is defined
        pstyle = f"height: {str(height)}px" if height is not None else ''

        # calculate the width in percent
        width = 100 * (value_now / value_max)

        # define text to be displayed in the progress bar
        display_val = (
            display_val if display_val is not None else f"{width:.1f}%"
        )

        ptext = "justify-content-center d-flex position-absolute w-100"

        with div(className=cls(self.classes.progress), style=pstyle):
            div(
                span(
                    display_val,
                    cls=ptext,
                    style='' if height is None else f"font-size:{height*4}%"),
                role="progressbar",
                style=f"width:{width}%;height:100%;",
                aria_valuenow=str(value_now),
                aria_valuemin=str(value_min),
                aria_valuemax=str(value_max),
                className=cls(
                    self.classes.progress_bar,
                    bar_cls if bar_cls is not None else ''))
