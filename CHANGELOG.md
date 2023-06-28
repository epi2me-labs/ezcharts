# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
