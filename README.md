ezCharts
==========

(Apologies to non-US English speakers).

ezCharts is a Python library for creating and rendering charts through [eCharts](https://echarts.apache.org/).
Plots can be contructed through an API similar to [seaborn](https://seaborn.pydata.org/).

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

The base library in ezCharts does not try to hide eCharts API in order that everything
follows the eCharts [documention](https://echarts.apache.org/en/option.html#title). An
API is provided that mirrors the [seaborn](https://seaborn.pydata.org/) API to allow
creation of common plot types without knowledge of eCharts.


Contributing
------------

The aim is to slowly build out the seaborn-like API with functionality required
whilst reusuing as much of the seaborn data analysis code as possible. Function
stubs have been added according to the v0.11.2 documentation. The seaborn
requirement is however pinned to v0.12.0b2. In implementing a plotting function
the 0.12.0 series should be followed.
