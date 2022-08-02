"""Get document and helper tags with sensible defaults."""
from dominate.tags import body, head, meta, script, style, title


SCRIPT_KWARGS = dict(__pretty=False, type='text/javascript')
STYLE_KWARGS = dict(__pretty=False)


def report_body(scroll_spy=True, **kwargs):
    """Dis em body."""
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
