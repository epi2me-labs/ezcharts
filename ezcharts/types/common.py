"""Dumping ground for types."""

from typing import List, Literal, NewType, Union

from ezcharts.util import MagicObject


# placeholder types
Color = NewType("Color", str)  # maybe others
number = NewType("number", Union[int, float])
Rich = NewType("RichText", MagicObject)


# TODO: this came from Axis, the top level options has something
#       similar with a few attributes missing
class TextStyle(MagicObject):
    """Typedef for styling text."""

    color: Color
    fontStyle: Literal["normal", "italic", "oblique"]
    fontWeight: Literal[
        "normal", "bold", "bolder", "lighter", 100, 200, 300, 400, 500]
    fontFamily: Literal["sans-sarif", "serif", "monospace"]
    fontSize: number
    align: Literal["left", "center", "right"]
    verticalAlign: Literal["top", "middle", "bottom"]
    lineHeight: number
    backgroundColor: Union[str, MagicObject]
    borderColor: Color
    borderWidth: number
    borderType: Union[
        Literal["solid", "dashed", "dotted"], number, List[number]]
    borderDashOffset: number
    borderRadius: number
    padding: Union[number, List[number]]
    # TODO: should we be inheriting ShadowStyle?
    shadowColor: Color
    shadowBlur: number
    shadowOffsetX: number
    shadowOffsetY: number
    width: number
    height: number
    textBorderColor: Color
    textBorderWidth: number
    textborderType: Union[
        Literal["solid", "dashed", "dotted"], number, List[number]]
    textBorderDashOffset: number
    textShadowColor: Color
    textShadowBlue: number
    textShadowOffsetX: number
    textShadowOffsetY: number
    overflow: Literal["none", "truncate", "break", "breakAll"]
    ellipsis: str
    rich: MagicObject


class LineStyle:
    """Typedef for styling lines."""

    ...


class AreaStyle:
    """Typedef for styling areas."""

    ...


class ShadowStyle:
    """Typedef for styling shadows."""

    ...


class Handle:
    """Typedef for a handle."""

    ...


class AxisLine(MagicObject):
    """Typedef for axis lines."""

    show: bool
    onZero: bool
    onZeroAxisIndex: number
    symbol: Union[str, List]
    symbolSize: List[number]
    symbolOffset: Union[List[number], number]
    lineStyle: LineStyle


class AxisTick(MagicObject):
    """Typedef for axis ticks."""

    show: bool
    alignWithLabel: bool
    interval: number  # also function
    inside: bool
    length: number
    lineStyle: LineStyle


class AxisMinorTick(MagicObject):
    """Typedef for axis minor ticks."""

    show: bool
    splitNumber: number
    length: number
    lineStyle: LineStyle


class AxisLabel(TextStyle):
    """Typedef for axis labels."""

    show: bool
    interval: number  # also function
    inside: bool
    rotate: number
    margin: number
    formatter: str  # also function
    showMinLabel: bool
    showMaxLabel: bool
    hideOverlap: bool


class PointerLabel(TextStyle):
    """Typedef for pointer labels."""

    show: bool
    precision: Union[number, str]
    formatter: str  # also function
    margin: number


class SplitLine(MagicObject):
    """Typdef for splitlines (lines on graph background)."""

    show: bool
    interval: number  # also function
    lineStyle: LineStyle


class MinorSplitLine(MagicObject):
    """Typdef for minor splitlines (lines on graph background)."""

    show: bool
    lineStyle: LineStyle


class SplitArea(MagicObject):
    """Typedef for splitareas (see documentation)."""

    interval: number  # also function
    show: bool
    areaStyle: AreaStyle


class Data(MagicObject):
    """Data specification.

    https://echarts.apache.org/en/option.html#xAxis.data
    """

    value: str
    textStyle: TextStyle


class AxisPointer(MagicObject):
    """Typedef for axis pointer."""

    show: bool
    type: Literal["line", "shadow", "none"]
    snap: bool
    z: number
    label: PointerLabel
    lineStyle: LineStyle
    shadowStyle: ShadowStyle
    triggerTooltip: bool
    value: number
    status: Literal["show", "hide"]
    handle: Handle


class Axis(MagicObject):
    """Typedef of an Axis."""

    id: str
    show: bool
    gridIndex: number
    alignTicks: bool
    offset: number
    type: Literal["category", "value", "time", "log"]
    name: str
    nameLocation: Literal["end", "start", "middle", "center"]
    nameTextStyle: TextStyle
    nameGap: number
    nameRotate: number
    inverse: bool
    boundaryGap: Union[bool, List]
    min: Union[number, str]  # also function
    max: Union[number, str]
    scale: bool
    splitNumber: number
    minInterval: number
    maxInterval: number
    interval: number
    logBase: number
    silent: bool
    triggerEvent: bool
    axisLine: AxisLine
    axisTick: AxisTick
    minorTick: AxisMinorTick
    axisLabel: AxisLabel
    splitLine: SplitLine
    minorSplitLine: MinorSplitLine
    splitArea: SplitArea
    data: Union[List, Data]
    axisPointer: AxisPointer
    zlevel: number
    z: number


class XAxis(Axis):
    """Typedef for the abscissa."""

    position: Literal["top", "bottom"]


class YAxis(Axis):
    """Typedef for the ordinate."""

    position: Literal["left", "right"]
