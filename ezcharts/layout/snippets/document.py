"""Get document and helper tags with sensible defaults."""
from dominate.tags import body, head, meta

SCRIPT_KWARGS = dict(__pretty=False, type='text/javascript')
STYLE_KWARGS = dict(__pretty=False)


class DefaultBody(body):
    """Report body element."""

    def __init__(
        self,
        scroll_spy: bool = True,
        **kwargs
    ) -> None:
        """Create tag."""
        if scroll_spy:
            kwargs = {
                "data-bs-spy": "scroll",
                "data-bs-offset": "-150",
                **kwargs
            }
        super().__init__(
            tagname='body', **kwargs)


class DefaultHead(head):
    """Report body element."""

    def __init__(
        self,
        **kwargs
    ) -> None:
        """Create tag."""
        super().__init__(tagname='head', **kwargs)
        with self:
            meta(charset="utf-8")
            meta(
                name="viewport",
                content="width=device-width, initial-scale=1")
