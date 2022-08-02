"""Useful reusable functions."""
import sass
from dominate.tags import body, head, meta, script, style, title
from dominate.util import raw


SCRIPT_KWARGS = dict(__pretty=False, type='text/javascript')
STYLE_KWARGS = dict(__pretty=False)


def inline(path):
    """Return a file as a string."""
    with open(path, 'r', encoding='utf-8') as content:
        return raw(content.read())


def transpile(path):
    """Compile scss to css."""
    # with open(path, 'r') as content:
    #     scss = content.read()
    compiled = sass.compile(
        filename=path, output_style='compressed')
    return raw(compiled)


def report_body(scroll_spy=True, **kwargs):
    """Dis em bodied"""
    if scroll_spy:
        kwargs = {
            "data-bs-spy": "scroll",
            "data-bs-offset": "-150"
        }
    _body = body(**kwargs)
    return _body


def report_head(report_title: str):
    """Get ahead!"""
    _head = head()
    with _head:
        meta(charset="utf-8")
        meta(name="viewport", content="width=device-width, initial-scale=1")
        title(report_title)
    return _head


def scriptd(content):
    """Return a script with defaults."""
    return script(content, **SCRIPT_KWARGS)


def styled(content):
    """Return a stylesheet with defaults."""
    style(content, **STYLE_KWARGS)


def write_report(path, document):
    """Write a report to file."""
    with open(path, 'w', encoding='utf-8') as out:
        out.write('<!DOCTYPE html>')
        out.write(document.render())
