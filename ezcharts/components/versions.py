"""A reusable software versions table."""
import os

from ezcharts.layout.snippets.table import DataTable


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
