"""Plotting functionality via echarts."""

from ezcharts.plots._model import EChartsOption


class Plot(EChartsOption):
    """Main plotting interface."""

    def to_json(self, **kwargs):
        """Create a json representation of options."""
        return self.json(exclude_unset=True)

    def add_series(self, spec):
        """Add a series to chart."""
        if self.series is None:
            self.series = list()
        self.series.append(spec)
