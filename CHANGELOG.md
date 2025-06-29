# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.14.1]
### Fixed
- LeadSummary balances columns aware of `None` values.
- Reports now include Arial and Sans-serif font options, to improve appearance when Noto Sans is unavailable.

## [v0.14.0]
### Changed
- Percentage of reads aligned histogram x-axis limits are now default 0 to 100.
- Accuracy histogram x-axis limits are now default 80 to 100.
### Added
- Download button in sankey plot.
- DataTables.from_pandas takes `use_headers` kwarg.
- DataTables `sortable` added to API.
- DetailsTable, LeadSummary, WorkflowQCBanner components for reports.
- Added `page_number` attribute to the report, which if `True` adds a styled footer to the report containing the page number.
- Add `make_table` to create QC control checks tables.
### Fixed
- Sankey now scales down until it hits 800px, it then scrolls. This avoids overflowing the right of the screen on narrow viewports.
- Sequence summary read length N50 incorrectly displayed minimum read length, it now correctly shows the N50.
- Sequence summary component alignment and coverage plots amended to also work with histogram data as input, example added to demo. [CW-5838]


## [v0.13.1]
### Fixed
- SeqSummary read_length_plot_binwidth override not working in v.13.0.

## [v0.13.0]
### Changed
- Updated relational plot APIs: Now support bokeh_kwargs, allowing customization of bokeh.figure during initialization.
- ONT style update with re-branding
- MSA start:end now uses bed file format
### Added
- Read length plot x-axis initial range max can be set with `read_length_quantile_xend`.

## [v0.12.0]
### Added
- `si_format` function for formatting numbers.
- SeqSummary histograms show a warning when no aligned reads to plot.
- Added parameter to set data type in `read_files`.
### Changed
- Reports have a maximum width.
- Boxplot hover shows summary stats.
- SeqSummary histograms' axis defaults increased to be inclusive of maximum values.
### Fixed
- Regression squishing ECharts plots when a different tab is selected.
- SeqSummary histograms' median value no longer converted to an integer.
- SeqSummary min axis range works when set to 0.
- Boxplots can be made with a single array of values.
- Boxplot colours now cycle through the palette for large datasets.
- Icons on pass, fail and unknown badges have a fixed position to prevent overlapping with text.

## [v0.11.5]
### Fixed
- ValueError: invalid literal for int() with base 10 in `base_yield_plot`
### Changed
- Clarify SeqSummary read alignment title and axis label.

## [v0.11.4]
### Fixed
- Added setuptools to conda package requirements to unbreak package distribution.
### Added
- Added setuptools to python package requirements as it is required for runtime use of pkg_resources.

## [v0.11.3]
### Fixed
- load_modkit_summary function shows the threshold value of any modified base.
### Changed
- ONT reports now have burger style navigation.
- SeqSummary dropdown menu shows samples in order.
- Seqviz plot now displays enzymes in a multi-select box.
### Added
- `additional_styles` dictionary parameter to allow more style options of div in `EZchart()`
- SeqSummary read_length_plot binwidth can be overridden from default.

## [v0.11.2]
### Changed
- Bokeh plots featuring more than one data series will automatically have a legend.
### Fixed
- Tooltips not displaying meaningful values.

## [v0.11.1]
### Changed
- Hide service workflow parameters from ParamsTable.

## [v0.11.0]
### Changed
- Bumped minor version as 0.10.2 should have been 0.11.0.
### Fixed
- Transparent lines/points plotted in relational plots.
- Add `hover` back to bokeh toolbox.
- `SeqCompare` not working with histograms and line charts from `BokehPlots`.
### Removed
- BcftoolsStats component until it is updated to use BokehPlot.

## [v0.10.2]
### Changed
- Now uses Bokeh as plotting backend for `histplot()`, `lineplot()` and `scatterplot()`.
- Reduced some padding and margins to make the report more compact.
### Fixed
- Sankey top rank (superkingdom) counts being affected by subrank filtering.
- Sankey samples in dropdown now appear in alphabetical order.
### Added
- `PlotMetaData` function to plot barcharts using a JSON file of nextflow workflow metadata.

## [v0.10.1]
### Fixed
- The maximum read length reported in the sub-title of `components.fastcat.read_length_plot()` being one bp too large.
### Changed
- Data types in demo changed to dropdown list.
- MSA now accepts start and end co-ordinates for partial sequence visualisation.

## [v0.10.0]
### Added
- MSA visualisation with [pymsaviz](https://github.com/moshi4/pyMSAviz/)
- Plasmid visualisation with [seqviz](https://github.com/Lattice-Automation/seqviz)

## [v0.9.2]
### Changed
- Navigation bar links now replaced with a dropdown list of links to sections on the report.

## [v0.9.1]
### Added
- Ability to change height of seq summary plots.
### Changed
- Added argument to skip the plotting of accuracy and coverage histograms (`alignment_stats`) in `SeqSummary` and `SeqCompare`.
### Fixed
- `color` option not working in `SeqSummary`
- Resizing behaving oddly in some cases

## [v0.9.0]
### Added
- `SeqCompare` function to compare individual metrics across samples.
### Changed
- Allow color override for fastcat standard plots.
- ONT skin.
- `SeqSummary` can display the histograms for accuracy and coverage, if available in the histogram directory.
### Fixed
- `bcfstats` component crashing when the `bcftools stats` output has missing sections.

## [v0.8.0]
### Added
- Required argument `workflow_version` to `LabsReport` and `ONDReport`.
- Argument to `fastcat.load_stats()` to select target columns to load.
- Two different functions: `load_fastcat()` and `load_bamstats()` to load per-read-stats.
- A function to concatenate categorical columns: `concat_dfs_with_categorical_columns()`.
- Tests for functions related with `SeqSummary`.
- Decorator for plotting a message when the plot fails.
- `ezc.boxplot` is now implemented to produce boxplots.
### Changed
- Refactor `SeqSummary`.
### Removed
- Mention of the `nextflow run ... --help` command from the report footer.
- `histogram_stats_dir` in `SeqSummary`. Histograms data is input using `seq_summary`.


## [v0.7.10]
### Fixed
- `barplot` tries to create a stacked barplot when `dodge=False` without a `hue`.

## [v0.7.9]
### Fixed
- Error raised when reading an empty CSV with the `SeqSummary` component.

## [v0.7.8]
### Added
- Nested bar charts by setting `nested_x=True` in `barplot()`.
- SeqSummary ability to read precomputed fastcat histogram data.
- Upgraded sample card functionality.

### Fixed
- Regression causing empty line or scatter plots when no `hue` variable was provided.
- `lineplot()` and `scatterplot()` not handling the `palette` argument correctly.
- Mixed `start_time` offset bug in SeqSummary.

## [v0.7.7]
### Fixed
- `lineplot()` and `scatterplot()` failing with numerical `hue` values.

## [v0.7.6]
### Fixed
- Spuriously scrolling to top of page when clicking on ellipsis in pagination links below data tables.

### Added
- Total yield as additional metric below title in `fastcat.SeqSummary.base_yield_plot()`.

## [v0.7.5]
### Fixed
- Font family declaration for Ubuntu
- VersionList output

## [v0.7.4]
### Fixed
- Regression squishing ECharts plots when a different tab is selected.

## [v0.7.3]
### Fixed
- List group colour

## [v0.7.2]
### Changed
- OND styling
- `"epi2melabs"` is now the default `theme` for `EZChart()`.

## [v0.7.1]
### Fixed
- `barplot()` failing with numerical group names (i.e. values of categorical axis).

## [v0.7.0]
### Removed
- `BokehChart` class for adding Bokeh plots to the enclosing `dominate` context. This can be done with `EZChart` now (just as with ECharts plots).

## [v0.6.8]
### Fixed
- Error in importing clinvar-annotated VCFs with multiple `GENEINFO` entries.

## [v0.6.7]
### Changed
- Now uses static JS asset for Nextclade table.
- Now uses Bokeh as plotting backend for `barplot()`.
- Parameters of `fastcat.read_length_plot()`: removed `min_len` and `max_len` and added `quantile_limits`.

## [v0.6.6]
### Fixed
- `clinvar.load_vcf` crashes with empty clinvar vcf files.

## [v0.6.5]
### Fixed
- Regression of `fastcat.SeqSummary` no longer being able to load a list of fastcat / bamstats input files.

## [v0.6.4]
### Fixed
- Fix conda build missing dependencies

## [v0.6.3]
### Added
- bcfstats loader from aplanat.

## [v0.6.2]
### Added
- ClinVar vcf table loader.

## [v0.6.1]
### Fixed
- Update license name in meta.yaml required for conda.

## [v0.6.0]
### Fixed
- Modkit summary loader converting canonical C counts to modC.
### Changed
- Improve modkit bedMethyl to account both spacers or a single one.
- Read length plot in `SeqSummary` now also displays the minimum read length in the title sub-text.
### Added
- Bokeh as alternative plotting utility.

## [v0.5.4]
### Fixed
- Sankey uses the right total value to calculate percentages when there are more than one sample.
- `fastcat.read_length_plot()` now actually uses the parameters `min_len`, `max_len`, `xlim`, and `bin_width`.

## [v0.5.3]
### Fixed
- Pin pendatic to <2.0.0 for conda.

## [v0.5.2]
### Fixed
- SeqSummary crashing when passing a dataframe as input.

## [v0.5.1]
### Fixed
- Data loaders not handling files with header-only appropriately.
- `add_missing_intervals` crashes with unsorted dataframes and is now generic.

## [v0.5.0]
### Added
- Data load utilities for modkit, DSS, mosdepth and bamstats.
- Test data for the new loaders.
- Add karyomap plot (binned karyotype heatmap).

## [v0.4.0]
### Added
- Add sunburst plots.
- Sankey plot for metagenomic / taxonomic data.
### Fixed
- `SeqSummary` read quality histograms only showing one bar which is too thin to see when all reads have the same quality score.

## [v0.3.7]
### Added
- `isolate_context` context manager that prevents `dominate` from adding items to the enclosing context.
- `sep` in read_files to customise the default delimiter when reading tables.
- OND style
### Changed
- Nextclade widget updated to 1.0.4
- To more sensible behaviour governing when to use scientific notation for axis tick labels.

## [v0.3.6]
### Changed
- Now draws a maximum of 1,000 instead of 10,000 points in the `fastcat.SeqSummary` yield plot.
- Display and centre all axis tick labels in heatmaps

## [v0.3.5]
### Fixed
- A regression that prevented using lists of lists as dataset sources.
### Changed
- Now uses a dropdown menu instead of regular tabs for `fastcat.SeqSummary` if there are multiple samples.
### Added
- Add stack option to barplot.
- Add export button to datatables.
- Add function to plot cartesian heatmaps.

## [v0.3.4]
### Added
- Marker size and type in relational plots.

## [v0.3.3]
### Fixed
- CI issues with v0.3.2 causing a partial release.

## [v0.3.2]
### Fixed
- Allow axis label gap fix for numberical axis type.
- Bug caused when there were spaces or other special characters in tab headers.
### Addded
- Color palette chooser.
- Dataframes to tables (`DataTable.from_pandas()`).
- Dicts to tables (`DataTable.from_dict()`).
- Option for dropdown menus to update the title of the dropdown tab when selecting an item.
- Multivariate histograms.
### Removed
- Dataview no longer enabled by default as its somewhat flakey.

## [v0.3.1]
### Fixed
- Dropdown menus now work.
- Issue where numbers in progress bars would show too many decimals.

### Changed
- Tab "activeness" is now automatically calculated.

## [v0.3.0]
### Changed
- Bootstrap updated to 5.3.0
### Added
- Create fastcat.SeqSummary from bamstats data.
- Snippet for offcanvas

## [v0.2.6]
### Fixed
- Intro content added to header instead of main.

## [v0.2.5]
### Added
- More colours to EPI2ME Labs template.
- BaseReport class

## [v0.2.4]
### Added
- Scientific notation to axis labels.
### Fixed
- yield plot fix to prevent too much data being plotted.

## [v0.2.3]
### Changed
- All plots now have a toolbox by default.
### Added
- Histogram and barplot with seaborn API.
- Fastcat sequence summary component.
- Some overriding of eCharts defaults.
- Added ecStat 1.2.0 to vendor resources
- Adding paging options to DataTable
- CLI now configures logging.

## [v0.2.2]
### Added
- Ideogram - function to draw ideograms from user provided data.
- JSCode class for javascript code snippets.
### Fixed
- Cleaned up inclusion of data resources.

## [v0.2.1]
### Fixed
- conda requirements

## [v0.2.0]
### Added
- Automatic eCharts API code generation.
- Make project skeleton for plotting and reports.
- Sketch a few seaborn-like plotting functions, stub others.
- Base dominate reporting functionality.
- Port several canned-components from aplanat.
- Bootstrap cards and progress-bar snippet.

## [v0.1.0]
### Added
- Empty project
