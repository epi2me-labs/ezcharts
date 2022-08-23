"""A base snippet to inherit from."""
from dataclasses import dataclass
from uuid import uuid4

from dominate.tags import html_tag


@dataclass
class IClasses:
    """Snippet html classes."""

    ...


@dataclass
class IStyles:
    """Snippet html classes."""

    ...


class BaseSnippet(html_tag):
    """Base snippet."""

    TAG: str = 'div'

    def __init__(
        self,
        *args,
        styles: dataclass = IClasses(),
        classes: dataclass = IStyles(),
        **kwargs
    ):
        """Create snippet."""
        self.styles = styles
        self.classes = classes
        self.uid = self.__class__.__name__ + '_' + str(
            uuid4()).replace("-", "")
        kwargs.update({'tagname': self.TAG})
        super().__init__(
            *args,
            **kwargs,
            id=self.uid)
