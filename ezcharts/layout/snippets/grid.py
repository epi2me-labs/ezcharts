"""Get default grid layout."""
from dominate.tags import html_tag


class Grid(html_tag):
    """A styled div tag for creating css-grids."""

    def __init__(
        self,
        columns: int = 2,
        column_gap: int = 10,
        row_gap: int = 20
    ) -> None:
        """Create tag."""
        styles = ' '.join([
            "display: grid;",
            f"grid-template-columns: repeat({columns}, 1fr);",
            "grid-template-rows: repeat(1, 1fr);",
            f"grid-column-gap:{column_gap}px;",
            f"grid-row-gap: {row_gap}px;"
        ])
        super().__init__(
            tagname='div', className="report-grid", style=styles)
