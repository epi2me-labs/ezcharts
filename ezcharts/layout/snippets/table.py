"""Get default table layouts."""
from typing import List, Optional, Union

from dominate.tags import script, table, tbody, td, th, thead, tr
from jinja2 import BaseLoader, Environment

from ezcharts.layout.base import BaseSnippet, IClasses, IStyles
from ezcharts.layout.util import cls


class ITableClasses(IClasses):
    """Table html classes."""

    container: str = cls("table-responsive")
    table: str = cls("table", "table-striped", "table-hover")


class ITableStyles(IStyles):
    """Table inline css styles."""

    ...


class DataTable(BaseSnippet):
    """A styled datatable wrapped in a div."""

    TAG = 'div'
    DATATABLE_INIT = """
        new simpleDatatables.DataTable('#{{ id }}_inner', {
            searchable: true,
            columns: [
                { select: 2, sort: 'desc' },
            ]
        })
    """

    def __init__(
        self,
        headers: List[str],
        styles: ITableStyles = ITableStyles(),
        classes: ITableClasses = ITableClasses(),
    ) -> None:
        """Create table."""
        super().__init__(
            styles=styles,
            classes=classes,
            className=classes.container)

        with self:
            with table(id=self.uid + '_inner', className=self.classes.table):
                self.head = thead()
                with self.head:
                    with tr():
                        for _header in headers:
                            th(_header, scope="col")
                self.body = tbody()
            rtemplate = Environment(loader=BaseLoader()).from_string(
                self.DATATABLE_INIT)
            rendered = rtemplate.render(id=self.uid)
            script(rendered)

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
                    td(str(column))
        return row
