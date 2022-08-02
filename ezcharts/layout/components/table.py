"""Get default table layouts."""
import json
import os
import uuid
from typing import List, NamedTuple, Optional, Union

from dominate.tags import div, script, table, tbody, td, th, thead, tr

from jinja2 import BaseLoader, Environment


SCRIPT_DATATABLE_TEMPL = """
    const dataTable_{{ id }} = new simpleDatatables.DataTable('#{{ id }}', {
        searchable: true,
        columns: [
            { select: 2, sort: 'desc' },
        ]
    })
"""


def report_table_row(
    title: Optional[str],
    columns: List[Union[str, int, float]]
) -> tr:
    """
    Generate a table row component, compatible with
    report_table.
    """
    row = tr()
    with row:
        if title:
            th(title, scope="row1")
        for column in columns:
            td(str(column))
    return row


class ITableReturn(NamedTuple):
    """Specifies the return types for report_table."""
    main: div
    head: thead
    body: tbody


def report_table(
    headers: List[str],
    container_classes: str = "table-responsive",
    table_classes: str = "table table-striped table-hover"
) -> ITableReturn:
    """
    Generate a table component with labs-bootstrap
    styling by default. Headers can provided via the
    so-named argument. Rows can provided by nesting under
    the returned body attribute, as per usual.

    :returns: The containing div element and the thead and tbody
        table elements.
    """
    uid = 'table' + '_' + str(uuid.uuid4()).replace('-', '_')
    _table = div(className=container_classes)
    with _table:
        with table(id=uid, className=table_classes):
            _table_head = thead()
            with _table_head:
                with tr():
                    for _header in headers:
                        th(_header, scope="col")
            _table_body = tbody()
        rtemplate = Environment(loader=BaseLoader()).from_string(
            SCRIPT_DATATABLE_TEMPL)
        rendered = rtemplate.render(id=uid)
        script(rendered)
    return ITableReturn(_table, _table_head, _table_body)


#
# These functions below were lifted from aplanat and probably need reworking.
#
def version_table(
    versions_path: str
) -> ITableReturn:
    """Create a table of software versions."""
    if os.path.isdir(versions_path):
        version_files = [
            os.path.join(versions_path, x)
            for x in os.listdir(versions_path)]
    elif os.path.isfile(versions_path):
        version_files = [versions_path]
    else:
        raise IOError('`versions` should be a file or directory.')
    versions_table = report_table(['Name', 'Version'])
    for fname in version_files:
        try:
            with open(fname, 'r', encoding='utf-8') as fh:
                with versions_table.body:
                    for line in fh.readlines():
                        name, version = line.strip().split(',')
                        report_table_row(
                            title=None, columns=[name, version])
        except Exception:
            pass
    return versions_table


def params_table(
    params_file: str
) -> ITableReturn:
    """Create a workflow parameter report from a JSON file."""
    if not os.path.isfile(params_file):
        raise IOError('`params` should be a JSON file.')
    param_table = report_table(['Key', 'Value'])
    with open(params_file, encoding='utf-8') as f:
        data = json.load(f)
        with param_table.body:
            for k, v in data.items():
                report_table_row(title=None, columns=[k, str(v)])
    return param_table
