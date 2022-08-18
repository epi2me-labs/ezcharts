"""Get default table layouts."""
from typing import List, Optional, Union
import uuid

from dominate.tags import div, script, table, tbody, td, th, thead, tr
from jinja2 import BaseLoader, Environment


class DataTable(div):
    """A styled datatable wrapped in a div."""

    DATATABLE_INIT = """
        new simpleDatatables.DataTable('#{{ id }}', {
            searchable: true,
            columns: [
                { select: 2, sort: 'desc' },
            ]
        })
    """

    def __init__(
        self,
        headers: List[str],
        container_classes: str = "table-responsive",
        table_classes: str = "table table-striped table-hover"
    ) -> None:
        """Create tag."""
        super().__init__(
            tagname='div', className=container_classes)
        uid = 'table' + '_' + str(uuid.uuid4()).replace('-', '_')

        with self:
            with table(id=uid, className=table_classes):
                self.head = thead()
                with self.head:
                    with tr():
                        for _header in headers:
                            th(_header, scope="col")
                self.body = tbody()
            rtemplate = Environment(loader=BaseLoader()).from_string(
                self.DATATABLE_INIT)
            rendered = rtemplate.render(id=uid)
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
