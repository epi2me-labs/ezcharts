ezCharts
==========

(Apologies to non-US English speakers).

ezCharts is a Python library for creating and rendering charts through [eCharts](https://echarts.apache.org/).
Plots can be contructed through an API similar to [seaborn](https://seaborn.pydata.org/).

Additionally, ezCharts ships with a layout system built around [dominate](https://github.com/Knio/dominate/),
providing a framework for creating static HTML reports via a declarative syntax.

Using the charting and layout functionality, a library of report components is
provided in the domain of bioinformatics analysis and Nanopore sequencing.


Installation
------------

ezCharts is easily installed in the standard Python tradition:

    git clone --recursive https://github.com/epi2me-labs/ezcharts.git
    cd ezcharts
    pip install -r requirements.txt
    python setup.py install

or via pip:

    pip install ezcharts.


Usage
-----

**Plots**

The base library in ezCharts does not try to hide eCharts API in order that everything
follows the eCharts [documention](https://echarts.apache.org/en/option.html#title). The
API was in fact constructed from an API schema encoded in the source code of the documentation
site --- users can therefore follow the eCharts documentation to construct charts
with ezCharts. This differs from the [pyecharts](https://pyecharts.org/) library which
obfuscates the eCharts API.

*eCharts API*

The library contains a single `Plot` class for constructing charts. Instances of this
class have an attribute hierarchy that mirrors the eCharts [Option API](https://echarts.apache.org/en/option.html).
Attributes can be set by providing a ditionary, runtime type checking ensures that
child attributes match the Option API:

```
from ezcharts.plots import Plot

plt = Plot()
plt.xAxis = dict(name="My Variable", type="categorical")
``` 

It is not currently possible to set child attributes without first setting a parent, i.e.
the following is **not** possible:


```
from ezcharts.plots import Plot

plt = Plot()
plt.xAxis.name = "My Variable"
```

This may change in a later release.

TODO: How to display a plot


*Seaborn API*

An API is provided that mirrors the [seaborn](https://seaborn.pydata.org/) API to allow
creation of common plot types without knowledge of eCharts. This currently has minimal
functionality that will be added to over time.

**Layout**

The layout functionality of ezCharts uses bootstrap scripting and styling be default,
but permits any level of customisation. Snippets provide simple re-usable bits of HTML
that are pre-styled, such as Tabs or tables.

TODO: simple demo, then refer to demo.py


**Components**

Components provide higher order application-specific layouts that may also include
charts and light data processing capabilities, such as Read Length graphs.

TODO: link to components, list common ones.

Contributing
------------

The aim is to slowly build out the seaborn-like API with functionality required
whilst reusuing as much of the seaborn data analysis code as possible. Function
stubs have been added according to the v0.11.2 documentation. The seaborn
requirement is however pinned to v0.12.0b2. In implementing a plotting function
the 0.12.0 series should be followed.
