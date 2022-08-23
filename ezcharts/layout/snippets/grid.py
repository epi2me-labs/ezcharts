"""Get default grid layout."""
from dominate.tags import style

from ezcharts.layout.base import BaseSnippet, IClasses, IStyles
from ezcharts.layout.util import css, render_template


class IGridClasses(IClasses):
    """Section html classes."""

    container: str = ""


class IGridStyles(IStyles):
    """Section inline css styles."""

    container: str = css(
        "display: grid",
        "grid-template-rows: repeat(1, 1fr)",
        "grid-template-columns: repeat(2, 1fr)",
        "grid-column-gap: 10px",
        "grid-row-gap: 20px")


class Grid(BaseSnippet):
    """A styled div tag for creating css-grids."""

    TAG = 'div'
    GRID_TEMPLATE = """
        #{{grid_id}} {
            {{ styles }}
            {% if c %}
            grid-template-columns: repeat({{ c }}, 1fr)
            {% endif %}
        };

        // Responsive css grids
        @media only screen and (max-width: 800px) {
            #{{grid_id}} {
                grid-template-columns: repeat(1, 1fr) !important;
            }
        }
    """

    def __init__(
        self,
        columns: int = None,
        styles: IGridStyles = IGridStyles(),
        classes: IGridClasses = IGridClasses()
    ) -> None:
        """Create css grid."""
        super().__init__(
            styles=styles,
            classes=classes,
            className=classes.container)

        with self:
            style(render_template(
                self.GRID_TEMPLATE,
                grid_id=self.uid,
                styles=self.styles.container,
                c=columns))
