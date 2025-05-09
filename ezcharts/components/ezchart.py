"""Get ezchart containers."""
from abc import ABC, abstractmethod
import json

from dominate.tags import script
from dominate.util import raw

from ezcharts.layout.base import Snippet
from ezcharts.layout.util import render_template
from ezcharts.plots import BokehPlot, Plot
from ezcharts.plots.util import finalise


def EZChart(
    plot,
    theme: str = 'epi2melabs',
    width: str = '100%',
    height: str = '500px',
    additional_styles: dict = None
):
    """Wrap an ECharts or Bokeh plot in a div."""
    if isinstance(plot, BokehPlot):
        finalise(plot._fig)
        return _BokehChart(
            plot, theme=theme, width=width, height=height,
            additional_styles=additional_styles)
    elif isinstance(plot, Plot):
        return _EChart(
            plot, theme=theme, width=width, height=height,
            additional_styles=additional_styles)
    else:
        raise ValueError(f"`EZChart()` called with argument of unexpected type: {plot}")


class _ReportChart(ABC, Snippet):
    """ABC for `div` containers containing ECharts or Bokeh plots."""

    TAG = 'div'

    @abstractmethod
    def __init__(self, width, height, class_name, additional_styles=None):
        """Set width and height of plot."""
        style_dict = {
            "width": width,
            "height": height,
            **(additional_styles or {})
        }

        style_str = "; ".join(
            f"{key}:{value}" for key, value in style_dict.items())

        Snippet.__init__(
            self,
            styles=None,
            classes=None,
            className=class_name,
            style=style_str)


class _BokehChart(_ReportChart):
    """Wraps a Bokeh plot in a div."""

    def __init__(
        self,
        plot,
        theme: str = 'epi2melabs',
        width: str = '100%',
        height: str = '500px',
        additional_styles=None
    ) -> None:
        """Add placeholder div for BokehChart.

        The JS for all Bokeh plots will be added at report generation; no need to do
        anything besides keeping a ref to the plot at this point.
        """
        super().__init__(
            width, height, class_name="bokeh-chart-container",
            additional_styles=additional_styles)
        self.plot = plot


class _EChart(_ReportChart):
    """Wraps an ECharts plot in a div."""

    def __init__(
        self,
        plot,
        theme: str = 'epi2melabs',
        width: str = '100%',
        height: str = '500px',
        additional_styles=None
    ) -> None:
        """Create a div and script tag for initialising the plot."""
        # `class_name="echarts-chart-container"` here is required for resizing the chart
        # when a different tab is selected (c.f. `update_charts_on_tab_change()` in
        # `data/scripts/epi2melabs.js`)
        super().__init__(
            width, height, class_name="echarts-chart-container",
            additional_styles=additional_styles)

        with self:
            script(raw(render_template(
                """
                var chart_{{ id }} = echarts.init(
                    dom=document.getElementById('{{ id }}'),
                    theme='{{ t }}',
                    opts={renderer: '{{ c.renderer }}'});
                var opt_{{ id }} = {{ j | replace('"',"'") | safe }};
                chart_{{ id }}.setOption(opt_{{ id }});
                {% if w.endswith('%') %}
                    window.addEventListener('resize', function(){
                        chart_{{ id }}.resize();
                    })
                {% endif %}
                chart_{{ id }}.resize()
                """,
                c=plot, j=plot.to_json(), t=theme,
                w=width, id=self.uid)))


class EZChartTheme(script):
    """Loads an echarts theme in a script tag."""

    def __init__(
        self,
        theme: str
    ) -> None:
        """Load theme."""
        super().__init__(tagname='script')
        with self:
            raw(render_template(
                """
                echarts.registerTheme(
                    '{{ n.themeName }}',
                    {{ t | replace(\'"\',"\'") | safe }}.theme);
                """,
                n=theme, t=json.dumps(theme)))


# No module demo here as entrypoint is in `plots.demo`.
