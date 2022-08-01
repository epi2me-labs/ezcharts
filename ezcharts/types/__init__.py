"""Definitions of charts setOption hierarchy."""

import json
from typing import List, Literal

import pyecharts

from ezcharts.types.common import number, XAxis, YAxis
from ezcharts.types.series import AllSeriesTypes
from ezcharts.util import MagicObject


class Plot(pyecharts.charts.base.Base):
    """Main plotting interface."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super().__init__(*args, **kwargs)
        # we can't just subclass because fields conflict. (And this
        # is cleaner, not like bokeh attaching things everywhere).
        self.opt = SetOptions(parent=self)

    class Encoder(json.JSONEncoder):
        """JSON encoder of self."""

        def default(self, obj):
            """Return a boring message."""
            return "A Plot"

    def to_json(self, **kwargs):
        """Create a json representation of options."""
        return json.dumps(self.opt, cls=self.Encoder, **kwargs)


class SetOptions(MagicObject):
    """Basic plot."""

    title: MagicObject
    legend: MagicObject
    grid: MagicObject
    xAxis: XAxis
    yAxis: YAxis
    polar: MagicObject
    radiusAxis: MagicObject
    angleAxis: MagicObject
    radar: MagicObject
    dataZoom: MagicObject
    visualMap: MagicObject
    tooltip: MagicObject
    axisPointer: MagicObject
    toolbox: MagicObject
    brush: MagicObject
    geo: MagicObject
    parallel: MagicObject
    parallelAxis: MagicObject
    singleAxis: MagicObject
    timeline: MagicObject
    graphic: MagicObject
    calender: MagicObject
    dataset: MagicObject
    aria: MagicObject
    series: List[AllSeriesTypes]
    darkMode: MagicObject
    color: MagicObject
    backgroundColor: MagicObject
    textStyle: MagicObject
    animation: bool
    animationThreshold: number
    animationDuration: number  # also function
    animationEasing: str  # lots available
    animationDelay: number  # also function
    animationDurationUpdate: number  # also function
    animationEastingUpdate: str  # lots available
    animationDelayUpdate: number
    stateAnimation: MagicObject
    blendMode: Literal["source-over", "lighter"]
    hoverLayerThreshold: int
    useUTC: bool
    options: MagicObject
    media: MagicObject

    def __init__(self, *args, parent=None, **kwargs):
        """Initialise the class."""
        super().__init__(*args, **kwargs)
        self._parent = parent
        # using .update() here sidesteps all typing and __attr__ voodoo
        self.update({'series': list()})

    def __setattr__(self, attr, value):
        """Syncronise attributes with options in parent."""
        if attr == 'series':
            raise TypeError(
                "Cannot set 'series' with `.series`, use add_series instead.")

        super().__setattr__(attr, value)
        if self._parent is not None:
            self._parent.options.update(self)

    def add_series(self, spec):
        """Add a series to chart."""
        self.series.append(spec)
