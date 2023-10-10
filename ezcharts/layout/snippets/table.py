"""Get default table layouts."""
from collections.abc import Iterable
from typing import List, Optional, Union

from dominate.tags import button, script, table, tbody, td, th, thead, tr
from dominate.util import raw
import pandas as pd

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
        headers: Optional[List[str]] = None,
        page_length: Optional[int] = 10,
        paging: Optional[bool] = True,
        searchable: Optional[bool] = True,
        file_name: Optional[str] = 'datatable-export',
        export: Optional[bool] = False,
        classes: ITableClasses = ITableClasses(),
    ) -> None:
        """
        Create table.

        The default constructor should only be used in special cases. Use the
        alternative constructors `.from_pandas()` or `.from_dict()` instead.

        :param headers: List of strings for headers or multiple lists for multilevel
            headers. If `None`, no header is produced, defaults to `None`
        :param page_length: Page length of the table, defaults to `10`
        :param paging: Whether to allow paging, defaults to `True`
        :param classes: HTML classes, defaults to `ITableClasses()`
        """
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
                if headers is not None:
                    with self.head:
                        # check for multi-level headers (i.e. if `headers` is a list of
                        # lists)
                        if not self._is_multilevel_header(headers):
                            # single-level header --> wrap in list
                            headers = [headers]
                        for header_level in headers:
                            with tr():
                                for _header in header_level:
                                    th(_header, scope="col")
                self.body = tbody()

            # Prepare table
            datatable_render = """
                var {{ id }}_table = new simpleDatatables.DataTable( \
                    '#{{ id }}_inner', { \
                    searchable: {{ searchable }}, \
                    pageLength: {{ page_length }}, \
                    paging: {{ paging }} \
                })"""

            if export:
                datatable_render, exportCSVButton = self._export_table(datatable_render)
            else:
                exportCSVButton = None

            script(raw(render_template(
                datatable_render,
                id=self.uid, paging=str(paging).lower(),
                searchable=str(searchable).lower(), page_length=page_length,
                button_id=exportCSVButton, file_name=file_name)))

    def _is_multilevel_header(self, headers: list) -> bool:
        """Check if header list is a multi-level header (i.e. a list of lists).

        :param headers: List of strings for headers or multiple lists for multilevel
            headers.
        :raises ValueError: Raise error when `headers` contains iterables as well as
            non-iterables (e.g. lists and also strings)
        :return: `bool` whether the header is multilevel
        """
        # we got a multilevel header if all items in `headers` are non-string iterables
        # (lists, tuples, etc.)
        headers_iterables = [
            isinstance(header, Iterable) and not isinstance(header, str)
            for header in headers
        ]
        if all(headers_iterables):
            return True
        # if we have a mixture of iterables and non-iterables, throw an error
        if any(headers_iterables):
            raise ValueError(
                f"Header list `{headers}` contains both iterables and non-iterables."
            )
        return False

    def add_row(
        self,
        title: Optional[str],
        columns: List[Union[str, int, float]]
    ) -> tr:
        """Add a row of cells to the table."""
        with self.body:
            with tr() as row:
                if title is not None:
                    th(title, scope="row1")
                for column in columns:
                    td(raw(str(column)))
        return row

    def _export_table(self, datatable_render) -> str:
        """Add a button for exporting the datatable."""
        # Add button
        exportCSVButton = f"{self.uid}_exportButton"
        button(
            "Export CSV", id=exportCSVButton, type="button",
            className=cls("btn btn-outline-primary"))
        datatable_render = datatable_render + \
            """
            document.getElementById('{{ button_id }}').addEventListener('click',\
            () => {{ id }}_table.export({ \
            type: 'csv', download: true, filename: '{{file_name}}'}))
            """
        return datatable_render, exportCSVButton

    @classmethod
    def from_pandas(
        cls,
        df: pd.DataFrame,
        use_index: bool = True,
        **kwargs
    ):
        """
        Create a `DataTable` from a `pandas.DataFrame`.

        Multi-level columns are supported but multi-level indices are currently not.

        :param df: `pandas.DataFrame`
        :param use_index: Include `DataFrame` index column in table, defaults to `True`
        :return: `DataTable`
        """
        nlevels = df.columns.nlevels
        headers = list(df.columns)

        if nlevels > 1:
            # multiindex columns --> convert into list of tuples
            headers = []
            for i in range(nlevels):
                col_lvl = df.columns.get_level_values(i).to_list()
                if use_index:
                    if i == nlevels - 1:
                        # Set the index name in the bottom level of the table columns.
                        col_lvl.insert(0, df.index.name or 'index')
                    else:
                        col_lvl.insert(0, '')
                headers.append(col_lvl)

        else:
            if use_index:
                headers = [df.index.name or "index", *headers]
        dtable = cls(headers=headers, **kwargs)

        for idx, *row in df.itertuples():
            title = idx if use_index else None
            dtable.add_row(title=title, columns=row)

        return dtable

    @classmethod
    def from_dict(cls, d: dict, use_index: bool = True, **kwargs):
        """Create `DataTable` from a dictionary.

        Uses `pd.DataFrame.from_dict()` and creates the DataTable from the resulting
        `pd.DataFrame`. Be aware that `pd.DataFrame.from_dict()` by default assumes
        "column orientation" (i.e. each key--value pair denotes a column name and
        collection of column values). You can change this behaviour with
        `orient="index"`.

        :param d: Input dictionary; values should be list/tuple-like collections but not
            other dictionaries. Scalar values will cause an error in
            `pd.DataFrame.from_dict()`.
        :param use_index: Include index column of generated DataFrame in table, defaults
            to `True`
        :return: `DataTable`
        """
        df = pd.DataFrame.from_dict(d, **kwargs)
        return cls.from_pandas(df, use_index=use_index)
