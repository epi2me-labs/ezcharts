from dominate.tags import div


def report_grid(
    columns: int = 2,
    column_gap: int = 10,
    row_gap: int = 20
) -> div:
    """Generate a div that applies css-grid styling."""
    styles = ' '.join([
        "display: grid;",
        f"grid-template-columns: repeat({columns}, 1fr);",
        f"grid-template-rows: repeat(1, 1fr); grid-column-gap:{column_gap}px;",
        f"grid-row-gap: {row_gap}px;"
    ])
    return div(className="report-grid", style=styles)
