# ezCharts

(Apologies to non-US English speakers).

ezCharts is a Python library for creating and rendering charts through [eCharts](https://echarts.apache.org/)
or [Bokeh](https://docs.bokeh.org/en/latest/).
Plots can be constructed through an API similar to [seaborn](https://seaborn.pydata.org/).

Additionally, ezCharts ships with a layout system built around [dominate](https://github.com/Knio/dominate/),
providing a framework for creating static HTML reports via a declarative syntax.

Using the charting and layout functionality, a library of report components is
provided in the domain of bioinformatics analysis and Nanopore sequencing.


## Installation

ezCharts is easily installed in the standard Python tradition:

    git clone --recursive https://github.com/epi2me-labs/ezcharts.git
    cd ezcharts
    pip install -r requirements.txt
    python setup.py install

or via pip:

    pip install ezcharts


## Usage

The `Plot()` API in ezCharts mirrors the eCharts API in order that everything
follows the eCharts [documention](https://echarts.apache.org/en/option.html). The
API was in fact constructed from an API schema encoded in the source code of the documentation
site. Users can therefore follow the eCharts documentation to construct charts
with ezCharts. This differs from the [pyecharts](https://pyecharts.org/) library which
adds a layer of indirection.

### eCharts plots

The library contains a `Plot` class for constructing plots using eCharts. Instances of this
class have an attribute hierarchy that mirrors the eCharts [Option API](https://echarts.apache.org/en/option.html).
Attributes can be set by providing a dictionary, runtime type checking ensures that
child attributes match the Option API:

```
from ezcharts.plots import Plot
from ezcharts.components.reports.comp import ComponentReport

plt = Plot()
plt.xAxis = dict(name="Day", type="category")
plt.yAxis = dict(type="value")
plt.dataset = [dict(
    dimensions = ['Day', 'Rabbits'],
    source = [
        ['Monday', 150],
        ['Tuesday', 230],
        ['Wednesday', 224],
        ['Thursday', 218],
        ['Friday', 135],
        ['Saturday', 147],
        ['Sunday', 260]
    ]
)]
plt.series = [dict(type='line')]
ComponentReport.from_plot(plt, "tmp.html")
```

Up to the the final line, the code here mirrors exactly the javascript eCharts
API. Note, many of the examples in the eCharts API set `data` items on the
`xAxis` and `series` attributes. However the eCharts
[dataset](https://echarts.apache.org/handbook/en/concepts/dataset)
documentation advises setting data within the `dataset` attribute; doing so
provides an experience somewhat akin to
[ggplot2](https://ggplot2.tidyverse.org/index.html) in R or
[seaborn](https://seaborn.pydata.org/) in Python. The primary use is to create
additional datasets through [data
transforms](https://echarts.apache.org/handbook/en/concepts/data-transform):

```
plt = Plot()
plt.xAxis = dict(name="Day", type="category")
plt.yAxis = dict(type="value")
plt.dataset = [...]  # as above

plt.add_dataset({
    'id': 'filtered',
    'fromDatasetIndex': 0,
    'transform': [{
        'type': 'filter',
        'config': {'dimension': 'Rabbits', 'gt': 200}
    }]
})

plt.series = [dict(type='line', datasetIndex=1)]
```

The above example shows the use of a simple filter to plot only a subset of the
data. More usually transforms can be used to plot multiple series based on a
facet of the data.

The example also shows use of the convenience method `.add_dataset()`: this is
provided to ensure the provided dictionary is type-checked against the eCharts
API. The alternative would be to call `.append({...})` on the `plt.dataset`
attribute. However, this is at risk of error. Similarly, the `.add_series()`
method exists to attach additional series to the chart.

**Gotchas**

It is not currently possible to set child attributes without first setting a
parent, i.e. the following is **not** possible:

```
from ezcharts.plots import Plot

plt = Plot()
plt.xAxis.name = "My Variable"
```

This may change in a later release.

Rendering a chart may result in in JSON encoding errors. To resolve this,
amendments are needed to `excharts.plots._base` to define how types can be
encoded to JSON.

### Bokeh plots

Since v0.6.0, [Bokeh](https://docs.bokeh.org/en/latest/) can be used as
alternative plotting backend. To this end, a wrapper class `BokehPlot` exists.
The Bokeh figure instance can be accessed under the `_fig` attribute (see example below).

```
from ezcharts.plots import BokehPlot
from ezcharts.components.reports.comp import ComponentReport

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
rabbits = [150, 230, 224, 218, 135, 147, 260]

plt = BokehPlot(
    x_range=days, title="some title", x_axis_label="Day", y_axis_label="Rabbits"
)
plt._fig.vbar(x=days, top=rabbits, width=0.9)

ComponentReport.from_plot(plt, "tmp.html")
```

### Seaborn API

A higher level API is provided that mirrors the [seaborn](https://seaborn.pydata.org/) API
to allow creation of common plot types without knowledge of eCharts. This
currently has minimal functionality that will be added to over time. The idea
is that eventually most plotting can be performed through this API without
requiring use of the `Plot` class.

```
import ezcharts as ezc
from ezcharts.components.reports.comp import ComponentReport
import seaborn as sns

tips = sns.load_dataset("tips")

plt = ezc.scatterplot(data=tips, x="total_bill", y="tip", hue="size")
ComponentReport.from_plot(plt, "tmp.html")
```

### Layout

The layout functionality of ezCharts uses bootstrap scripting and styling by
default, but permits any level of customisation. Snippets provide simple
re-usable bits of HTML that are pre-styled, such as tabs and tables.

```
import ezcharts as ezc
from ezcharts.components.ezchart import EZChart
from ezcharts.layout.snippets import DataTable, Tabs

from ezcharts.components.reports.labs import BasicReport

from dominate.tags import p
import seaborn as sns

tips = sns.load_dataset("tips")
tips["size"] = tips["size"].astype(str)

report = BasicReport("test report")

plt = ezc.scatterplot(data=tips, x="total_bill", y="tip", hue="size")

with report.add_section("test section", "test"):
    tabs = Tabs()
    with tabs.add_tab("First tab"):
        EZChart(plt)
    with tabs.add_tab("Second tab"):
        p("Some text.")
        DataTable.from_pandas(tips)

report.write("tmp.html")
```

Note that `EZChart()` is required to add the plot to the enclosing `dominate`
context.

**Components**

Components provide higher level application-specific layouts (a table for
[Nextclade](https://clades.nextstrain.org/) results, for instance) that may also
include charts and light data processing capabilities (e.g. to parse and
visualise [fastcat](https://github.com/epi2me-labs/fastcat) output).

For a comprehensive showcase of current capabilities, please have a look at
`ezcharts/demo.py`.


## Contributing

The aim is to slowly build out both the seaborn-like API and the components
library with functionality required.

Much of the seaborn data analysis code can be reused. Function
stubs have been added according to the v0.11.2 documentation. The seaborn
requirement is however pinned to v0.12.0b2.  In implementing a plotting
function the 0.12.0 series should be followed.
