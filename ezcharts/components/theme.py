"""Re-usable external resources."""
from dominate.tags import div, img, script, style

from ezcharts.components.ezchart import EZChartTheme
from ezcharts.layout.resource import (
    base_body_resources, base_head_resources,
    ImageResource, ScriptResource, StyleResource, ThemeResource)
from ezcharts.layout.util import inline, load_json, transpile


class EPI2MELabsLogo(div):
    """Labs logo element."""

    def __init__(self) -> None:
        """Create a div with an SVG logo inside."""
        super().__init__(
            inline(ImageResource('LAB_logo.svg').data_file),
            tagname='div',
            style="width: 35px; height: 35px;",
            className="d-flex",
            alt="EPI2ME Labs Logo")


LAB_CSS = StyleResource(
    path='epi2melabs.scss',
    tag=style,
    loader=transpile)

LAB_JS = ScriptResource(
    path='epi2melabs.js',
    tag=script,
    loader=inline)

LAB_CHART_THEME = ThemeResource(
    path='epi2melabs.json',
    tag=EZChartTheme,
    loader=load_json)


LAB_head_resources = [LAB_CSS, *base_head_resources, LAB_CHART_THEME]
LAB_body_resources = [LAB_JS, *base_body_resources]


class ONDLogo(div):
    """OND logo element."""

    def __init__(self) -> None:
        """Create an img with the data URI logo."""
        super().__init__(
            inline(ImageResource('OND_logo.svg').data_file),
            tagname='div',
            style="width: 35px; height: 35px;",
            className="d-flex",
            alt="OND Logo")


# TODO: Create
OND_CSS = StyleResource(
    path='ond.scss',
    tag=style,
    loader=transpile)

OND_JS = ScriptResource(
    path='ond.js',
    tag=script,
    loader=inline)


OND_CHART_THEME = ThemeResource(
    path='ond.json',
    tag=EZChartTheme,
    loader=load_json)

OND_head_resources = [OND_CSS, *base_head_resources, OND_CHART_THEME]
OND_body_resources = [OND_JS, *base_body_resources]


class ONTLogo(img):
    """ONT logo element."""

    def __init__(self) -> None:
        """Create an img with the data URI logo."""
        super().__init__(
            inline(ImageResource('ONT_logo.txt').data_file),
            tagname='img',
            style="height: 35px;",
            className="d-flex",
            alt="ONT Logo")


# TODO: Create
ONT_CSS = StyleResource(
    path='epi2melabs.scss',
    tag=style,
    loader=transpile)

ONT_JS = ScriptResource(
    path='epi2melabs.js',
    tag=script,
    loader=inline)

ONT_head_resources = [ONT_CSS, *base_head_resources]
ONT_body_resources = [ONT_JS, *base_body_resources]
