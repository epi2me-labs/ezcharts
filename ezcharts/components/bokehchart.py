"""Get bokeh containers."""

from bokeh.embed import components
from dominate.tags import style
from dominate.util import raw

from ezcharts.layout.base import Snippet


class BokehChart(Snippet):
    """Wraps a Bokeh plot in a div."""

    TAG = "div"

    def __init__(
        self,
        plot,
        theme: str = None,
        width: str = "100%",
        height: str = "500px",
    ) -> None:
        """Create a div to be filled with the `bk-Figure` once the plot is rendered.

        The div can be filled in two ways. Either with `.render_plot()` (then it will
        contain both the `bk-Figure` div and accompanying script) or when `.write()` is
        called on the parent report. In the latter case, a single script section for all
        Bokeh figures is added to the header of the report and the div will contain only
        the `bk-Figure`.
        """
        super().__init__(
            styles=None,
            classes=None,
            className="bokeh-chart-container",
            style=f"width:{width}; height:{height};",
        )

        self.plot = plot

    @classmethod
    def render_plot(cls, plot):
        """Add the components of a Bokeh plot (script and div) to the enclosing context.

        This is useful if for any reason one wants to add a self-contained Bokeh chart
        into the parent context without relying on `Report.write()`. However, in most
        cases the preferred way of including a Bokeh plot is by instantiating an object
        of `BokehCharts`.
        """
        bokeh_script, bokeh_div = components(plot._fig)
        style(
            """
            .bk-Figure {
                width: 100%;
            }
            """
        )
        raw(bokeh_div)
        raw(bokeh_script)
