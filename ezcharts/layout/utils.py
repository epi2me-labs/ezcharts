"""Useful reusable functions."""
import sass

from dominate.util import raw


def inline(path):
    """Return a file as a string."""
    with open(path, 'r', encoding='utf-8') as content:
        return raw(content.read())


def transpile(path):
    """Compile scss to css."""
    compiled = sass.compile(
        filename=path, output_style='compressed')
    return raw(compiled)


def write_report(path, document):
    """Write a report to file."""
    with open(path, 'w', encoding='utf-8') as out:
        out.write('<!DOCTYPE html>')
        out.write(document.render())
