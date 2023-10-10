"""Re-usable external resources."""
from typing import Callable, Optional, Type

from bokeh.resources import INLINE as bk_inline
from dominate.tags import dom_tag, script, style
from dominate.util import raw
from pkg_resources import resource_filename

from ezcharts.layout.util import inline


class Resource:
    """Resource definition."""

    def __init__(
        self,
        path: Optional[str] = None,
        loader: Optional[Callable] = None,
        tag: Optional[Type[dom_tag]] = None,
        func: Optional[Callable] = None,
    ):
        """Construct resource from a path or a function.

        Either `path` or `func` must be given. `path` needs to point to a file in
        `ezcharts/data`, whereas `func` needs to be a callable that returns the resource
        as a string or dominate object.
        """
        # make sure we got only either a path or a function
        if not ((path is None) ^ (func is None)):
            raise ValueError("Resource needs either `path` or `func`.")
        # if we got a path, we require a loader as well
        if path is not None and loader is None:
            raise ValueError("`loader` is required when `path` was provided.")
        self.path = path
        self.loader = loader
        self.tag = tag
        self.func = func

    @property
    def data_file(self):
        """Filepath to resource data file."""
        return (
            resource_filename("ezcharts", f"data/{self.path}")
            if self.path is not None
            else None
        )

    def __call__(self):
        """Render the resource."""
        if self.path is not None:
            loaded = self.loader(self.data_file)
        elif self.func is not None:
            loaded = self.func()
        if self.tag:
            return self.tag(loaded)
        return loaded


def VendorResource(path=None, loader=inline, tag=None, func=None):
    """Fetch a vendor resource."""
    if path is not None:
        path = f"vendor/{path}"
    return Resource(path=path, loader=loader, func=func, tag=tag)


def ScriptResource(path=None, loader=inline, tag=None, func=None):
    """Fetch a script resource."""
    if path is not None:
        path = f"scripts/{path}"
    return Resource(path=path, loader=loader, func=func, tag=tag)


def ImageResource(path=None, loader=inline, tag=None, func=None):
    """Fetch an image resource."""
    if path is not None:
        path = f"images/{path}"
    return Resource(path=path, loader=loader, func=func, tag=tag)


def IconResource(path, loader=inline, tag=None):
    """Fetch an icon resource."""
    return Resource(f'icons/{path}', loader, tag)


def StyleResource(path=None, loader=inline, tag=None, func=None):
    """Fetch a style resource."""
    if path is not None:
        path = f"styles/{path}"
    return Resource(path=path, loader=loader, func=func, tag=tag)


def ThemeResource(path=None, loader=inline, tag=None, func=None):
    """Fetch a theme resource."""
    if path is not None:
        path = f"themes/{path}"
    return Resource(path=path, loader=loader, func=func, tag=tag)


def get_bokeh_js():
    """Get BokehJS library."""
    # make a dict mapping components to indices in `bk_inline.raw_js`
    comp_idx_dict = {comp: i for i, comp in enumerate(bk_inline.components_for('js'))}
    # we only support the basic Bokeh functionality for now (i.e. no widgets etc.)
    return raw(bk_inline.js_raw[comp_idx_dict["bokeh"]])


bokeh_js = ScriptResource(func=get_bokeh_js, tag=script)

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
    bokeh_js,
    echarts_js,
    datatables_js,
    datatables_css]

base_body_resources = [
    bootstrap_js]
