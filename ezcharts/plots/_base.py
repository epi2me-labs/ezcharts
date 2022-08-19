"""Base class for eCharts Options Model."""

from pydantic import BaseModel as PyDanticBase, Extra


class BaseModel(PyDanticBase, extra=Extra.forbid, validate_assignment=True):
    """Base class for eCharts Options."""
    # Note: this class's name in referenced in generate-model.py
    # TODO: can we overide getting of attributes to allow
    #       allow setting of children when parent isn't set.
    #       Simple __getattr__ isn't called :(
