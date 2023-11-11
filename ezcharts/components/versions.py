"""A reusable software versions table."""
import os

from ezcharts.layout.snippets.table import DataTable


#
# These functions below were lifted from aplanat and probably need reworking,
# should probably just inherit from DataTable above.
#

class VersionsTable(DataTable):
    """Display workflow params."""

    def __init__(
        self,
        versions_path: str,
        **kwargs
    ) -> None:
        """Create table."""
        if os.path.isdir(versions_path):
            version_files = [
                os.path.join(versions_path, x)
                for x in os.listdir(versions_path)]
        elif os.path.isfile(versions_path):
            version_files = [versions_path]
        else:
            raise IOError('`versions` should be a file or directory.')
        super().__init__(['Name', 'Version'], **kwargs)
        for fname in version_files:
            try:
                with open(fname, 'r', encoding='utf-8') as fh:
                    with self.body:
                        for line in fh.readlines():
                            name, version = line.strip().split(',')
                            self.add_row(
                                title=None, columns=[name, version])
            except FileNotFoundError:
                pass


class VersionsList():
    """Display workflow params as a more compact list."""

    def __init__(
        self,
        versions_path: str,
        **kwargs
    ) -> None:
        """Create string list."""
        if os.path.isdir(versions_path):
            version_files = [
                os.path.join(versions_path, x)
                for x in os.listdir(versions_path)]
        elif os.path.isfile(versions_path):
            version_files = [versions_path]
        else:
            raise IOError('`versions` should be a file or directory.')
        result = []
        for fname in version_files:
            try:
                with open(fname, 'r', encoding='utf-8') as fh:
                    for line in fh.readlines():
                        name, version = line.strip().split(',')
                        result.append(f"{name} ({version})")
            except FileNotFoundError:
                pass
        self.ver_string = ",".join(result)

    def __repl__(self):
        """Return version list."""
        return self.ver_string
