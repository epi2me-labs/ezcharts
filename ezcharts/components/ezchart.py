"""Get ezchart containers."""
import json

from dominate.tags import script
from dominate.util import raw

from ezcharts.layout.base import Snippet
from ezcharts.layout.util import render_template


class EZChart(Snippet):
    """Wraps an ezchart plot in a div."""

    TAG = 'div'

    def __init__(
        self,
        plot,
        theme: str,
        width: str = '100%',
        height: str = '500px'
    ) -> None:
        """Create a div and script tag for initialising the plot."""
        width = "100%"
        super().__init__(
            styles=None,
            classes=None,
            className="chart-container",
            style=f"width:{width}; height:{height};")

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


# No module demo here as method is directly on plot class.
