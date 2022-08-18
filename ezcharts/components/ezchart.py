"""Get ezchart containers."""
import json

from dominate.tags import div, script
from dominate.util import raw
from jinja2 import BaseLoader, Environment


class EZChart(div):
    """Wraps an ezchart plot in a div."""

    CHART_INIT = """
        var chart_{{ c.chart_id }} = echarts.init(
            dom=document.getElementById('{{ c.chart_id }}'),
            theme='{{ t }}',
            opts={renderer: '{{ c.renderer }}'});
        {% for js in c.js_functions.items %}
            {{ js }}
        {% endfor %}
        var opt_{{ c.chart_id }} = {{ j | replace('"',"'") | safe }};
        chart_{{ c.chart_id }}.setOption(opt_{{ c.chart_id }});
        {% if c.width.endswith('%') %}
            window.addEventListener('resize', function(){
                chart_{{ c.chart_id }}.resize();
            })
        {% endif %}
        chart_{{ c.chart_id }}.resize()
    """

    def __init__(
        self,
        plot,
        theme: str
    ) -> None:
        """Create a div and script tag for initialising the plot."""
        plot.width = "100%"
        super().__init__(
            tagname='div', id=plot.chart_id, className="chart-container",
            style="width:100%; height:500px;")
        rtemplate = Environment(
            loader=BaseLoader()).from_string(self.CHART_INIT)
        rendered = rtemplate.render(
            c=plot, j=plot.to_json(), t=theme)
        with self:
            script(rendered)


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
            rtemplate = Environment(
                loader=BaseLoader()).from_string(self.THEME_INIT)
            raw(rtemplate.render(n=theme, t=json.dumps(theme)))
