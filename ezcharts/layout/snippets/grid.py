"""Get default grid layout."""
from typing import Optional

from dominate.tags import style

from ezcharts.layout.base import IStyles, Snippet
from ezcharts.layout.util import css, render_template


class IGridStyles(IStyles):
    """Section inline css styles."""

    container: str = css(
        "display: grid",
        "grid-template-rows: repeat(1, 1fr)",
        "grid-template-columns: repeat(1, 1fr)",
        "grid-column-gap: 10px",
        "grid-row-gap: 20px")


class Grid(Snippet):
    """A styled div tag for creating css-grids."""

    TAG = 'div'

    def __init__(
        self,
        columns: Optional[int] = 2,
        styles: IGridStyles = IGridStyles()
    ) -> None:
        """Create css grid."""
        # We need to place the style tags before the
        # grid container otherwise contents won't
        # respect the rules properly. Therefore
        # we must generate an ID up front.
        uid = self.get_uid(self.__class__.__name__)

        # Adding extra style tags prior to the element
        # allows writing css in a conventional way,
        # rather than inline, permitting media queries.
        style(render_template(
            template=(
                """
                #{{grid_id}} {
                    {{ styles }}
                    {% if c %}
                    grid-template-columns: repeat({{ c }}, 1fr)
                    {% endif %}
                };
                """
            ),
            grid_id=uid,
            styles=styles.container,
            c=columns))

        # For some reason we have to break these up
        style(render_template(
            template=(
                """
                @media screen and (max-width: 800px) {
                    body #{{grid_id}} {
                        grid-template-columns: repeat(1, 1fr)
                    }
                }
                """
            ),
            grid_id=uid,
            styles=styles.container,
            c=columns))

        # Finally we call super to create the grid container
        # itself.
        super().__init__(id=uid, styles=styles, classes=None)
