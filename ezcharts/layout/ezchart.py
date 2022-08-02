from dominate.tags import div, script

from jinja2 import Environment, BaseLoader


SCRIPT_TEMPL = """
    var chart_{{ c.chart_id }} = echarts.init(
        document.getElementById(
            '{{ c.chart_id }}'),
            '{{ c.theme }}', {renderer: '{{ c.renderer }}'});
    {% for js in c.js_functions.items %}
        {{ js }}
    {% endfor %}
    var option_{{ c.chart_id }} = {{ c.json_contents | replace('"',"'") | safe }};
    chart_{{ c.chart_id }}.setOption(option_{{ c.chart_id }});
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


def get_ezchart_div(chart) -> div:
    """
    Generates a div tag that will act as a
    container for an echart instance.
    """
    chart.width = "100%"
    return div(
        id=chart.chart_id,
        className="chart-container",
        style="width:100%; height:500px;")


def get_ezchart_script(chart, templ=SCRIPT_TEMPL) -> script:
    """Generate a script tag that loads an ezchart within a target div."""
    rtemplate = Environment(loader=BaseLoader()).from_string(templ)
    rendered = rtemplate.render(c=chart)
    return script(rendered)


def ezchart(chart) -> div:
    """Generate tags necessary to render an echart instance."""
    chart._prepare_render()
    _container = get_ezchart_div(chart)
    with _container:
        get_ezchart_script(chart)
    return _container
