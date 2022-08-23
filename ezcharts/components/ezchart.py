"""Get ezchart containers."""
import json
from uuid import uuid4

from dominate.tags import div, script
from dominate.util import raw

from ezcharts.layout.util import render_template


class EZChart(div):
    """Wraps an ezchart plot in a div."""

    CHART_INIT = """
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
    """

    def __init__(
        self,
        plot,
        theme: str
    ) -> None:
        """Create a div and script tag for initialising the plot."""
        width = "100%"
        chart_id = str(uuid4()).replace("-", "")
        super().__init__(
            tagname='div', id=chart_id, className="chart-container",
            style="width:100%; height:500px;")
        with self:
            script(render_template(
                self.CHART_INIT,
                c=plot, j=plot.to_json(), t=theme,
                w=width, id=chart_id))


class EZChartTheme(script):
    """Loads an echarts theme in a script tag."""

    THEME_INIT = """
        echarts.registerTheme(
            '{{ n.themeName }}',
            {{ t | replace(\'"\',"\'") | safe }}.theme);
    """

    def __init__(
        self,
        theme: str
    ) -> None:
        """Load theme."""
        super().__init__(tagname='script')
        with self:
            raw(render_template(
                self.THEME_INIT,
                n=theme, t=json.dumps(theme)))
