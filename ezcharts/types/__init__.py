"""Definitions of charts setOption hierarchy."""

from typing import Literal

from ezcharts.types.common import number, XAxis, YAxis
from ezcharts.util import MagicObject


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
    series: MagicObject
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

    def __setattr__(self, attr, value):
        """Syncronise attributes with options in parent."""
        super().__setattr__(attr, value)
        if self._parent is not None:
            self._parent.options.update(self)
