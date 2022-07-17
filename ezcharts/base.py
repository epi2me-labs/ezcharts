"""Simple eCharts API."""

import json

from ezcharts.prodict import Prodict


class MagicObject(Prodict):
    """Nothing to see here."""

    def __getattr__(self, attr):
        """Get attribute, setting to default value if not preexisting.

        If the attribite is a known annotation, the corresponding
        constructor will be used, else a generic MagicObject will be
        created.
        """
        try:
            return self[attr]
        except KeyError:
            if self.has_attr(attr):
                construct = self.attr_type(attr)
            else:
                construct = MagicObject
            setattr(self, attr, construct())
            return super().__getattr__(attr)

    def to_json(self, **kwargs):
        """Create json represention for echarts."""
        return json.dumps(self, **kwargs)


class AxisSpec(MagicObject):
    """Specification of an Axis."""

    id: str
    show: bool
    gridIndex: int
    alignTicks: bool
    position: MagicObject
    offset: int
    type: str  # actually enum(str)
    name: str
    nameLocation: str  # actually enum(str)
    nameTextStyle: MagicObject
    nameGap: int
    nameRotate: MagicObject
    inverse: bool
    boundaryGap: MagicObject
    min: MagicObject
    max: MagicObject
    scale: bool
    splitNumber: int
    minInterval: int
    maxInterval: int
    interval: MagicObject
    logBase: int
    silent: bool
    triggerEvent: bool


class BasePlot(MagicObject):
    """Basic plot."""

    xAxis: AxisSpec
