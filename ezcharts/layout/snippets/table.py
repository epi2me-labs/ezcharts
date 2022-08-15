"""Get default table layouts."""
import json
import os
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


#
# These functions below were lifted from aplanat and probably need reworking,
# should probably just inherit from DataTable above.
#
def version_table(
    versions_path: str
) -> DataTable:
    """Create a table of software versions."""
    if os.path.isdir(versions_path):
        version_files = [
            os.path.join(versions_path, x)
            for x in os.listdir(versions_path)]
    elif os.path.isfile(versions_path):
        version_files = [versions_path]
    else:
        raise IOError('`versions` should be a file or directory.')
    versions_table = DataTable(['Name', 'Version'])
    for fname in version_files:
        try:
            with open(fname, 'r', encoding='utf-8') as fh:
                with versions_table.body:
                    for line in fh.readlines():
                        name, version = line.strip().split(',')
                        versions_table.add_row(
                            title=None, columns=[name, version])
        except FileNotFoundError:
            pass
    return versions_table


def params_table(
    params_file: str
) -> DataTable:
    """Create a workflow parameter report from a JSON file."""
    if not os.path.isfile(params_file):
        raise IOError('`params` should be a JSON file.')
    param_table = DataTable(['Key', 'Value'])
    with open(params_file, encoding='utf-8') as f:
        data = json.load(f)
        with param_table.body:
            for k, v in data.items():
                param_table.add_row(title=None, columns=[k, str(v)])
    return param_table
