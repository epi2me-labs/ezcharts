"""A reusable software details table."""

import logging

from dominate.tags import div, h6, table, td, th, thead, tr  # noqa: F401

from ezcharts.layout.base import Snippet

logger = logging.getLogger(__name__)


class ConfigurationTable(Snippet):
    """Display workflow params and software versions as more compact tables."""

    def __init__(
        self,
        versions,
        params,
        workflow_version,
        width=200,
        **kwargs,
    ) -> None:
        """Create details component.

        :param versions: dictionary with tools and versions.
        :param params: dictionary with params and values.
        :param workflow_version: Workflow version.
        :param width: width of the tables.

        """
        super().__init__(styles=None, classes=None)

        table_cls = "table table-sm table-striped small"
        table_style = "table-layout:fixed;"
        with div(cls="row"):
            with div(cls="col-xs-12 col-sm-6"):
                h6("Analysis tool versions", cls="fw-bold")
                with table(cls=table_cls, style=table_style):
                    thead(th("Software", style=f"width: {width}px;"), th("Version"))
                    tr(td("EPI2ME workflow version"), td(workflow_version))
                    for name, version in versions.items():
                        tr(td(name), td(version))
            with div(cls="col-xs-12 col-sm-6"):
                h6("Pertinent parameters", cls="fw-bold")
                with table(cls=table_cls, style=table_style):
                    thead(th("Parameter", style=f"width: {width}px;"), th("Value"))
                    for key, value in params.items():
                        param_value = value if value else ""
                        tr(
                            td(key, width=f"{width}px"),
                            td(str(param_value).replace(";", ", ")),
                        )
