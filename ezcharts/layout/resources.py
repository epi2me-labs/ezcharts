"""Re-usable external resources."""
from dataclasses import dataclass
from typing import Callable, List, Type

from dominate.tags import div, html_tag, img, script, style
from pkg_resources import resource_filename as res

from ezcharts.layout.utils import inline, transpile


EZ = 'ezcharts'
DATA = 'data'
IMAGES = f'{DATA}/images'
STYLES = f'{DATA}/styles'
SCRIPTS = f'{DATA}/scripts'
VENDOR = f'{DATA}/vendor'


#
# Common resources
#
@dataclass
class Resource:
    """Resource definition."""

    path: str
    tag: Type[html_tag]
    loader: Callable

    def __call__(self):
        """Render the resource."""
        self.tag(self.loader(self.path))


@dataclass
class Resources:
    """A collection of Resource objects."""

    head: List[Resource]
    body: List[Resource]


echarts_js = Resource(
    path=res(EZ, f'{VENDOR}/echarts.min.js'),
    tag=script,
    loader=inline
)

bootstrap_js = Resource(
    path=res(EZ, f'{VENDOR}/bootstrap-5.0.2/js/bootstrap.bundle.min.js'),
    tag=script,
    loader=inline
)

datatables_js = Resource(
    path=res(EZ, f'{VENDOR}/simple-datatables/simple-datatables.js'),
    tag=script,
    loader=inline
)

datatables_css = Resource(
    path=res(EZ, f'{VENDOR}/simple-datatables/simple-datatables.css'),
    tag=style,
    loader=inline
)

base_resources = Resources(
    head=[
        echarts_js,
        datatables_js,
        datatables_css
    ],
    body=[
        bootstrap_js
    ]
)


#
# Theme resources
#
@dataclass
class Theme:
    """Base theme definition."""

    js: Resource
    css: Resource
    logo: Type[html_tag]
    resources: Resources = base_resources

    def render_head_resources(self):
        """Write the head resources."""
        self.css()
        for h_tag in self.resources.head:
            h_tag()

    def render_body_resources(self):
        """Write the body resources."""
        self.js()
        for b_tag in self.resources.body:
            b_tag()


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

EPI2ME_labs_theme = Theme(
    js=LAB_JS,
    css=LAB_CSS,
    logo=EPI2MELabsLogo
)


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

OND_theme = Theme(
    js=LAB_JS,
    css=LAB_CSS,
    logo=ONDLogo
)


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

ONT_theme = Theme(
    js=LAB_JS,
    css=LAB_CSS,
    logo=ONTLogo
)
