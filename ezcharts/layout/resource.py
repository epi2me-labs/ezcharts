"""Re-usable external resources."""
from dataclasses import dataclass
from typing import Callable, Optional, Type

from dominate.tags import dom_tag, script, style
from pkg_resources import resource_filename as res

from ezcharts.layout.util import inline


EZ = 'ezcharts'
DATA = 'data'
IMAGES = f'{DATA}/images'
STYLES = f'{DATA}/styles'
SCRIPTS = f'{DATA}/scripts'
VENDOR = f'{DATA}/vendor'
THEMES = f'{DATA}/themes'


#
# Common resources
#
@dataclass
class Resource:
    """Resource definition."""

    path: str
    loader: Callable
    tag: Optional[Type[dom_tag]] = None

    def __call__(self):
        """Render the resource."""
        loaded = self.loader(self.path)
        if self.tag:
            return self.tag(loaded)
        return loaded


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

base_head_resources = [
    echarts_js,
    datatables_js,
    datatables_css
]

base_body_resources = [
    bootstrap_js
]
