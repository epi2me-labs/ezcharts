"""Re-usable external resources."""
from dominate.tags import div, img, script, style
from pkg_resources import resource_filename as res

from ezcharts.components.ezchart import EZChartTheme
from ezcharts.layout.resource import (
    base_body_resources, base_head_resources, EZ, IMAGES,
    Resource, SCRIPTS, STYLES, THEMES)
from ezcharts.layout.util import inline, load_json, transpile


#
# EPI2MELabs
#
class EPI2MELabsLogo(div):
    """Labs logo element."""

    def __init__(self) -> None:
        """Create a div with an SVG logo inside."""
        super().__init__(
            inline(res(EZ, f'{IMAGES}/LAB_logo.svg')),
            tagname='div',
            style="width: 35px; height: 35px;",
            className="d-flex",
            alt="EPI2ME Labs Logo")


LAB_CSS = Resource(
    path=res(EZ, f'{STYLES}/epi2melabs.scss'),
    tag=style,
    loader=transpile
)

LAB_JS = Resource(
    path=res(EZ, f'{SCRIPTS}/epi2melabs.js'),
    tag=script,
    loader=inline
)

LAB_CHART_THEME = Resource(
    res(EZ, f'{THEMES}/epi2melabs.json'),
    tag=EZChartTheme,
    loader=load_json
)


LAB_head_resources = [LAB_CSS, *base_head_resources, LAB_CHART_THEME]
LAB_body_resources = [LAB_JS, *base_body_resources]


#
# OND
#
class ONDLogo(img):
    """OND logo element."""

    def __init__(self) -> None:
        """Create an img with the data URI logo."""
        super().__init__(
            src=inline(res(EZ, f'{IMAGES}/OND_logo.txt')),
            tagname='img',
            style="height: 35px;",
            className="d-flex",
            alt="OND Logo")


# TODO: Create
OND_CSS = Resource(
    path=res(EZ, f'{STYLES}/epi2melabs.scss'),
    tag=style,
    loader=transpile
)

OND_JS = Resource(
    path=res(EZ, f'{SCRIPTS}/epi2melabs.js'),
    tag=script,
    loader=inline
)

OND_head_resources = [OND_CSS, *base_head_resources]
OND_body_resources = [OND_JS, *base_body_resources]


#
# ONT
#
class ONTLogo(img):
    """ONT logo element."""

    def __init__(self) -> None:
        """Create an img with the data URI logo."""
        super().__init__(
            src=inline(res(EZ, f'{IMAGES}/ONT_logo.txt')),
            tagname='img',
            style="height: 35px;",
            className="d-flex",
            alt="ONT Logo")


# TODO: Create
ONT_CSS = Resource(
    path=res(EZ, f'{STYLES}/epi2melabs.scss'),
    tag=style,
    loader=transpile
)

ONT_JS = Resource(
    path=res(EZ, f'{SCRIPTS}/epi2melabs.js'),
    tag=script,
    loader=inline
)

ONT_head_resources = [ONT_CSS, *base_head_resources]
ONT_body_resources = [ONT_JS, *base_body_resources]
