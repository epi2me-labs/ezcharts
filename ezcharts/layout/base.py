"""A base snippet to inherit from."""
from abc import ABC
from dataclasses import dataclass
import re
from uuid import uuid4

from dominate.tags import html_tag


@dataclass
class IDataClassMixin:
    """An inheritable dataclass."""

    ...


class IClasses(ABC, IDataClassMixin):
    """Snippet html classes."""

    ...


class IStyles(ABC, IDataClassMixin):
    """Snippet html styles."""

    ...


class Snippet(html_tag):
    """Base snippet."""

    TAG: str = 'div'

    def __init__(
        self,
        *args,
        styles,
        classes,
        **kwargs
    ):
        """Create snippet."""
        self.styles = styles
        self.classes = classes
        self.uid = self.get_uid(self.__class__.__name__)

        kwargs.update({'tagname': self.TAG})
        if not kwargs.get('id'):
            kwargs['id'] = self.uid

        super().__init__(*args, **kwargs)

    def get_uid(self, name: str) -> str:
        """Generate an ID."""
        # make sure `name` does not contain special characters so that the resulting uid
        # can be safely used in HTML `id` attributes
        if not re.match(r"^[a-zA-Z0-9_\-]+$", name):
            raise ValueError(
                "`name` cannot contain characters other than"
                "alphanumeric, '_', and '-'."
            )
        return name + '_' + str(uuid4()).replace("-", "")
