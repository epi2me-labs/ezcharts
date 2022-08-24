"""Base class for eCharts Options Model."""

import numpy as np
import pandas as pd
from pydantic import BaseModel as PyDanticBase, Extra


json_encoders = {
    pd.core.indexes.base.Index: lambda x: x.to_list(),
    pd.Series: lambda x: x.to_json(),
    np.ndarray: lambda x: x.tolist(),
    np.number: lambda x: float(x)}


class BaseModel(
        PyDanticBase, extra=Extra.forbid, validate_assignment=True,
        json_encoders=json_encoders):
    """Base class for eCharts Options."""
    # Note: this class's name in referenced in generate-model.py
    # TODO: can we overide getting of attributes to allow
    #       allow setting of children when parent isn't set.
    #       Simple __getattr__ isn't called :(
