"""Get default table layouts."""
from typing import List, Optional, Union

from dominate.tags import script, table, tbody, td, th, thead, tr
from dominate.util import raw

from ezcharts.layout.base import IClasses, Snippet
from ezcharts.layout.util import cls, render_template


class ITableClasses(IClasses):
    """Table html classes."""

    container: str = cls("table-responsive")
    table: str = cls("table", "table-striped", "table-hover")


class DataTable(Snippet):
    """A styled datatable wrapped in a div."""

    TAG = 'div'

    def __init__(
        self,
        headers: List[str],
        page_length: Optional[int] = 10,
        paging: Optional[bool] = True,
        classes: ITableClasses = ITableClasses(),
    ) -> None:
        """Create table."""
        super().__init__(
            styles=None,
            classes=classes,
            className=classes.container)

        with self:
            with table(
                id=self.uid + '_inner',
                className=self.classes.table
            ):
                self.head = thead()
                with self.head:
                    with tr():
                        for _header in headers:
                            th(_header, scope="col")
                self.body = tbody()
            script(render_template(
                """
                new simpleDatatables.DataTable('#{{ id }}_inner', {
                    searchable: true,
                    pageLength: {{ page_length }},
                    paging: {{ paging }},
                    columns: [
                        { select: 2, sort: 'desc' },
                    ]
                })
                """,
                id=self.uid,
                paging=str(paging).lower(),
                page_length=page_length))

    def add_row(
        self,
        title: Optional[str],
        columns: List[Union[str, int, float]]
    ) -> tr:
        """Add a row of cells to the table."""
        with self.body:
            with tr() as row:
                if title:
                    th(title, scope="row1")
                for column in columns:
                    td(raw(str(column)))
        return row
