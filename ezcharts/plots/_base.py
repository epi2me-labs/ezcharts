"""Base class for eCharts Options Model."""

import numpy as np
import pandas as pd
from pydantic import BaseModel as PyDanticBase, Extra

from ezcharts.plots.util import JSCode

json_encoders = {
    pd.core.indexes.base.Index: lambda x: x.to_list(),
    pd.Series: lambda x: x.to_json(),
    np.ndarray: lambda x: x.tolist(),
    np.number: lambda x: float(x),
    JSCode: lambda x: x.to_json()}


class BaseModel(
        PyDanticBase, extra=Extra.forbid, validate_assignment=True,
        json_encoders=json_encoders, arbitrary_types_allowed=True):
    """Base class for eCharts Options."""
    # Note: this class's name in referenced in generate-model.py
    # TODO: can we overide getting of attributes to allow
    #       allow setting of children when parent isn't set.
    #       Simple __getattr__ isn't called :(
