"""Useful reusable functions."""
import json
import os
from typing import Dict

from dominate.tags import script, style
from dominate.util import raw, text
from jinja2 import BaseLoader, Environment
from pkg_resources import resource_filename
import sass


def load_json(
    path: str
) -> Dict:
    """Return json file as a dict."""
    with open(path, 'r', encoding='utf-8') as content:
        return json.load(content)


def inline(
    path: str
) -> text:
    """Return a file as a string."""
    with open(path, 'r', encoding='utf-8') as content:
        return raw(content.read())


def resolve_import(path):
    """Find resource and return as list."""
    resolved = resource_filename('ezcharts', path)
    # Temporary measure
    if os.path.exists(resolved) and not os.path.isdir(resolved):
        return [[resolved]]
    return [[path]]


def transpile(path):
    """Compile scss to css."""
    compiled = sass.compile(
        filename=path,
        output_style='compressed',
        importers=[(0, resolve_import)])
    return raw(compiled)


def inline_script(path):
    """Inline a script from path."""
    return script(inline(path))


def transpile_style(path):
    """Transpile a stylesheet from path."""
    return style(transpile(path))


def write_report(path, document):
    """Write a report to file."""
    with open(path, 'w', encoding='utf-8') as out:
        out.write('<!DOCTYPE html>')
        out.write(document.render())


def render_template(template, **kwargs):
    """Render a jinja2 template."""
    rtemplate = Environment(
        loader=BaseLoader()).from_string(template)
    return rtemplate.render(**kwargs)


def cls(*classes: str) -> str:
    """Collect element classes from a list."""
    return ' '.join(classes)


def css(*styles: str) -> str:
    """Collect inline element styles from a list."""
    return ' '.join(s.strip(';') + ';' for s in styles)
