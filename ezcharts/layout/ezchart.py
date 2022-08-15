"""Get ezchart containers."""
from dominate.tags import div, script
from jinja2 import BaseLoader, Environment


CHART_TEMPL = """
    var chart_{{ c.chart_id }} = echarts.init(
        document.getElementById(
            '{{ c.chart_id }}'),
            '{{ c.theme }}', {renderer: '{{ c.renderer }}'});
    {% for js in c.js_functions.items %}
        {{ js }}
    {% endfor %}
    var opt_{{ c.chart_id }} = {{ c.json_contents | replace('"',"'") | safe }};
    chart_{{ c.chart_id }}.setOption(opt_{{ c.chart_id }});
    {% if c._is_geo_chart %}
        var bmap = chart_{{ c.chart_id }}
            .getModel().getComponent('bmap').getBMap();
        {% if c.bmap_js_functions %}
            {% for fn in c.bmap_js_functions.items %}
                {{ fn }}
            {% endfor %}
        {% endif %}
    {% endif %}
    {% if c.width.endswith('%') %}
        window.addEventListener('resize', function(){
            chart_{{ c.chart_id }}.resize();
        })
    {% endif %}
    chart_{{ c.chart_id }}.resize()
"""


class EZChart(div):
    """Wraps an ezchart plot in a div."""

    CHART_INIT = CHART_TEMPL

    def __init__(
        self,
        plot
    ) -> None:
        """Create a div and script tag for initialising the plot."""
        plot.width = "100%"
        plot._prepare_render()
        super().__init__(
            tagname='div', id=plot.chart_id, className="chart-container",
            style="width:100%; height:500px;")
        rtemplate = Environment(
            loader=BaseLoader()).from_string(self.CHART_INIT)
        rendered = rtemplate.render(c=plot)
        with self:
            script(rendered)
