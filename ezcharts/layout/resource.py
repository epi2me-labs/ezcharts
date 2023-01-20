"""Re-usable external resources."""
from dataclasses import dataclass
from typing import Callable, Optional, Type

from dominate.tags import dom_tag, script, style
from pkg_resources import resource_filename

from ezcharts.layout.util import inline


@dataclass
class Resource:
    """Resource definition."""

    path: str
    loader: Callable
    tag: Optional[Type[dom_tag]] = None

    @property
    def data_file(self):
        """Filepath to resource data file."""
        return resource_filename('ezcharts', f'data/{self.path}')

    def __call__(self):
        """Render the resource."""
        loaded = self.loader(self.data_file)
        if self.tag:
            return self.tag(loaded)
        return loaded


# dataclasses are annoying to derive


def VendorResource(path, loader=inline, tag=None):
    """Fetch a vendor resource."""
    return Resource(f'vendor/{path}', loader, tag)


def ScriptResource(path, loader=inline, tag=None):
    """Fetch a script resource."""
    return Resource(f'scripts/{path}', loader, tag)


def ImageResource(path, loader=inline, tag=None):
    """Fetch an image resource."""
    return Resource(f'images/{path}', loader, tag)


def StyleResource(path, loader=inline, tag=None):
    """Fetch a style resource."""
    return Resource(f'styles/{path}', loader, tag)


def ThemeResource(path, loader=inline, tag=None):
    """Fetch a theme resource."""
    return Resource(f'themes/{path}', loader, tag)


echarts_js = VendorResource(
    path='echarts.min.js',
    tag=script,
    loader=inline)

bootstrap_js = VendorResource(
    path='bootstrap-5.3.0/js/bootstrap.bundle.min.js',
    tag=script,
    loader=inline)

datatables_js = VendorResource(
    path='simple-datatables/simple-datatables.js',
    tag=script,
    loader=inline)

datatables_css = VendorResource(
    path='simple-datatables/simple-datatables.css',
    tag=style,
    loader=inline)

base_head_resources = [
    echarts_js,
    datatables_js,
    datatables_css]

base_body_resources = [
    bootstrap_js]
