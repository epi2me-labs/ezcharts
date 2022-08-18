"""Specification of all 'series' types.

These interfaces are the main way to create charts from data in eCharts.
"""

from typing import Literal, Union

from ezcharts.plots.util import MagicObject


class LineSeries(MagicObject):
    """Creating a LineSeries plot."""

    type: Literal["line"]
    id: str
    name: str
    ...


class BarSeries(MagicObject):
    """Creating a BarSeries plot."""

    type: Literal["bar"]
    id: str
    name: str
    ...


class PieSeries(MagicObject):
    """Creating a PieSeries plot."""

    type: Literal["pie"]
    id: str
    name: str
    ...


class ScatterSeries(MagicObject):
    """Creating a ScatterSeries plot."""

    type: Literal["scatter"]
    id: str
    name: str
    ...


class EffectScatterSeries(MagicObject):
    """Creating a EffectScatterSeries plot."""

    type: Literal["effectScatter"]
    id: str
    name: str
    ...


class RadarSeries(MagicObject):
    """Creating a RadarSeries plot."""

    type: Literal["radar"]
    id: str
    name: str
    ...


class TreeSeries(MagicObject):
    """Creating a TreeSeries plot."""

    type: Literal["tree"]
    id: str
    name: str
    ...


class TreeMapSeries(MagicObject):
    """Creating a TreeMapSeries plot."""

    type: Literal["treeMap"]
    id: str
    name: str
    ...


class SubBurstSeries(MagicObject):
    """Creating a SubBurstSeries plot."""

    type: Literal["subBurst"]
    id: str
    name: str
    ...


class BoxPlotSeries(MagicObject):
    """Creating a BoxPlotSeries plot."""

    type: Literal["boxPlot"]
    id: str
    name: str
    ...


class CandleStickSeries(MagicObject):
    """Creating a CandleStickSeries plot."""

    type: Literal["candleStick"]
    id: str
    name: str
    ...


class HeatMapSeries(MagicObject):
    """Creating a HeatMapSeries plot."""

    type: Literal["heatMap"]
    id: str
    name: str
    ...


class MapSeries(MagicObject):
    """Creating a MapSeries plot."""

    type: Literal["map"]
    id: str
    name: str
    ...


class ParallelSeries(MagicObject):
    """Creating a ParallelSeries plot."""

    type: Literal["parallel"]
    id: str
    name: str
    ...


class LinesSeries(MagicObject):
    """Creating a LinesSeries plot."""

    type: Literal["lines"]
    id: str
    name: str
    ...


class GraphSeries(MagicObject):
    """Creating a GraphSeries plot."""

    type: Literal["graph"]
    id: str
    name: str
    ...


class SankeySeries(MagicObject):
    """Creating a SankeySeries plot."""

    type: Literal["sankey"]
    id: str
    name: str
    ...


class FunnelSeries(MagicObject):
    """Creating a FunnelSeries plot."""

    type: Literal["funnel"]
    id: str
    name: str
    ...


class GaugeSeries(MagicObject):
    """Creating a GaugeSeries plot."""

    type: Literal["gauge"]
    id: str
    name: str
    ...


class PictorialBarSeries(MagicObject):
    """Creating a PictorialBarSeries plot."""

    type: Literal["pictorialBar"]
    id: str
    name: str
    ...


class ThemeRiverSeries(MagicObject):
    """Creating a ThemeRiverSeries plot."""

    type: Literal["themeRiver"]
    id: str
    name: str
    ...


class CustomSeries(MagicObject):
    """Creating a CustomSeries plot."""

    type: Literal["custom"]
    id: str
    name: str
    ...


AllSeriesTypes = Union[
    LineSeries, BarSeries, PieSeries, ScatterSeries, EffectScatterSeries,
    RadarSeries, TreeSeries, TreeMapSeries, SubBurstSeries, BoxPlotSeries,
    CandleStickSeries, HeatMapSeries, MapSeries, ParallelSeries,
    LinesSeries, GraphSeries, SankeySeries, FunnelSeries, GaugeSeries,
    PictorialBarSeries, ThemeRiverSeries, CustomSeries]
