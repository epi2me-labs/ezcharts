"""Run ezCharts demo."""
import argparse
import json

from bokeh.models.tickers import SingleIntervalTicker
from dominate.tags import div, h4, p
import numpy as np
import pandas as pd
from pkg_resources import resource_filename

import ezcharts as ezc
from ezcharts import util
from ezcharts.components.common import fasta_idx, HSA_CHROMOSOME_ORDER
from ezcharts.components.details import ConfigurationTable
from ezcharts.components.dss import load_dml, load_dmr
from ezcharts.components.ezchart import EZChart
from ezcharts.components.fastcat import load_bamstats_flagstat, load_stats
from ezcharts.components.fastcat import SeqCompare, SeqSummary
from ezcharts.components.lead_summary import LeadSummary, WorkflowQCBanner
from ezcharts.components.modkit import load_bedmethyl, load_modkit_summary
from ezcharts.components.mosdepth import load_mosdepth_regions, load_mosdepth_summary
from ezcharts.components.nextclade import NextClade, NXTComponent
from ezcharts.components.plotmetadata import PlotMetaData
from ezcharts.components.reports.labs import LabsReport
from ezcharts.components.theme import LAB_head_resources
from ezcharts.layout.snippets import DataTable
from ezcharts.layout.snippets import Grid
from ezcharts.layout.snippets import Progress
from ezcharts.layout.snippets import Stats
from ezcharts.layout.snippets import Tabs
from ezcharts.layout.snippets.cards import Cards
from ezcharts.layout.snippets.cards import ICard
from ezcharts.layout.snippets.offcanvas import IOffCanvasClasses, OffCanvas
from ezcharts.plots import BokehPlot, Plot
from ezcharts.plots.ideogram import ideogram
from ezcharts.plots.karyomap import karyomap
from ezcharts.plots.util import empty_plot, si_format


# Setup simple globals
WORKFLOW_NAME = 'wf-template'
WORKFLOW_VERSION = "v1.0.0"
REPORT_TITLE = f'{WORKFLOW_NAME}-report'


def main(args):
    """Demo for ezCharts functionality."""
    logger = util.get_named_logger("ezChrtDemo")

    # Good location to prepare plots
    logger.info('Building plots')

    # Example data
    raw_df = pd.DataFrame({
        # as laid out in echarts docs for a dataset
        'product': [
            'Matcha Latte', 'Milk Tea', 'Cheese Cocoa', 'Walnut Brownie'],
        '2015': [43.3, 83.1, 86.4, 72.4],
        '2016': [85.8, 73.4, 65.2, 53.9],
        '2017': [93.7, 55.1, 82.5, 39.1]
    })
    # how we'd likely normally have it
    example_df = raw_df.melt(
        id_vars=['product'], value_vars=['2015', '2016', '2017'],
        var_name='year', value_name='sales')

    def example_plot(style="line") -> Plot:
        """Create example plot."""
        if style == "line":
            plot = ezc.lineplot(data=example_df, x='year', y='sales', hue='product')
            # Bokeh attempts to plot years in line plots as continuous variables, so
            # we get xtick labels such as 2005,2005.5. This can be fixed by setting the
            # interval on the ticker to 1.
            plot._fig.xaxis.ticker = SingleIntervalTicker(interval=1)
        elif style == "scatter":
            plot = ezc.scatterplot(data=example_df, x='year', y='sales', hue='product')
            plot._fig.xaxis.ticker = SingleIntervalTicker(interval=1)
        elif style == 'histogram':
            hist_data = pd.DataFrame(
                        [np.random.normal(loc=10.0, size=1000),
                         np.random.normal(loc=12.0, size=1000),
                         np.random.normal(loc=14.0, size=1000)]).T
            hist_data.columns = ['sample1', 'sample2', 'sample3']
            plot = ezc.histplot(hist_data, bins=50, stat='proportion')

            plot._fig.xaxis.axis_label = 'Read length'
            plot._fig.yaxis.axis_label = 'Number of reads'
        elif style == "kdeplot":
            kde_data = np.random.normal(loc=10.0, size=1000)
            plot = ezc.kdeplot(kde_data)

            plot._fig.xaxis.axis_label = 'Read length'
            plot._fig.yaxis.axis_label = 'Density'
        elif style == "bar":
            plot = ezc.barplot(data=example_df, x='year', y='sales', hue='product')
        elif style == "heatmap":
            # make data a matrix like you would expect for a heatmap
            df = raw_df.set_index([raw_df.columns[0]])
            # set the names of the axes
            df = df.rename_axis("Product")
            df = df.rename_axis("Year", axis=1)
            plot = ezc.heatmap(data=df)
        elif style == "boxplot":
            # lets add some data to show off outliers
            raw_df['2024'] = [10.1, 100.0, 101.1, 99.8]
            df = pd.melt(raw_df, value_vars=['2015', '2016', '2017', '2024'])
            plot = ezc.boxplot(
                df, x="variable", y="value", order=['2024', '2017', '2015', '2016'])
        else:
            raise ValueError("Unknown plot style")

        title_text = f"Example {style} chart"

        # adding a title is different for echarts and bokeh
        if isinstance(plot, BokehPlot):
            plot._fig.title.text = title_text
        else:
            plot.title = {"text": title_text}

        return plot

    # Then, time to construct a report
    logger.info('Building report')

    # Example data
    client_fields_json = resource_filename('ezcharts', "data/test/client_fields.json")
    params = resource_filename('ezcharts', "data/test/params.json")
    versions = resource_filename('ezcharts', "data/test/versions/versions.txt")
    nxt_json = resource_filename('ezcharts', "data/test/nextclade.json")
    histogram_stats_dir = tuple(
        [
            resource_filename("ezcharts", "data/test/histogram_stats/sample_2"),
            resource_filename("ezcharts", "data/test/histogram_stats/sample_1"),
            resource_filename("ezcharts", "data/test/histogram_stats/empty_sample/"),
        ]
    )
    bamstats_histogram_stats_dir = tuple(
        [
            resource_filename("ezcharts", "data/test/bamstats_hist"),
        ]
    )

    # Create report
    # Note we need to add nextclade as a resource
    report = LabsReport(
        REPORT_TITLE, WORKFLOW_NAME, params, versions,
        workflow_version=WORKFLOW_VERSION,
        head_resources=[*LAB_head_resources, NXTComponent])

    # Add a header badge via a method on the report element.
    report.add_badge('Test badge', bg_class="bg-primary")

    # Make a progress bar for the median accuracy box
    median_accuracy = Progress(
            value_min=0,
            value_max=100,
            value_now=98.9,
            bar_cls="progress-bar-striped",
            height=50)

    # Add something directly to main_content.
    with report.main_content:
        # Stats is a snippet, but we could also just add any html
        # tags here. Snippets are little reusable portions of html,
        # styles and or scripts in python class format. They often
        # expose methods for adding content to them in a simple way.
        # E.g.
        Stats(
            columns=3,
            items=[
                ('1213986', 'Read count'),
                (median_accuracy, 'Median accuracy'),
                ('10213 bp', 'Some other stat')
            ])

    # Add sequence summary component
    with report.add_section('Sequence summaries', 'Summaries'):
        SeqSummary(
            seq_summary=histogram_stats_dir,
            color="#2a98b7",
            sample_names=tuple(['sample_2', 'sample_1', 'sample_3']),
            read_length_quantile_xend=0.99)
    with report.add_section('Sequence summaries alignment', 'Summaries aln'):
        SeqSummary(
            seq_summary=bamstats_histogram_stats_dir,
            color="#2a98b7",
            sample_names=tuple(['sample_1']),
            read_length_quantile_xend=0.99)
    with report.add_section('Compare Summaries', 'Compare'):
        SeqCompare(
            histogram_stats_dir,
            sample_names=tuple(['sample_2', 'sample_1', 'sample_3']),
            alignment_stats=False,
            color="#2a98b7",
        )

    # This also adds to main_content, but provides a nice
    # container snippet as a starting context.

    with report.add_section('Controls', 'Controls'):
        # This is an example of how to use bootstrap cards
        Cards(
            columns=2,
            items=[
                ICard(
                    head="Positive",
                    body="The positive passed",
                    footer="All postive controls within threshold",
                    classes="bg-success text-white"),
                ICard(
                    head="No Template Control",
                    body="The NTC failed",
                    footer="NTC outside set thresholds.",
                    classes="bg-danger text-white")])
        OffCanvas(
            label="More details (Offcanvas demo)",
            title="Details of Controls",
            body="You can put more details here....")

    # Add sample QC cards
    with report.add_section('QC', 'QC'):
        body_content = div(
            div("Column 1 Text", _class="col"),
            div("Column 2 Text", _class="col"),
            div("Column 3 Text", _class="col"),
            _class="row",
        )
        offcanvas_classes = IOffCanvasClasses()
        offcanvas_classes.offcanvas_button = "btn btn-detail float-end"

        sample_body = div(
            div(
                h4("Sample1"),
                p("This is a sample body.")
            )
        )
        ocps = {
            'label': "View details",
            'title': 'Sample detail',
            'body': sample_body,
            'classes': offcanvas_classes
        }
        Cards(
            columns=1,
            items=[
                ICard(
                    alias="Sample1",
                    barcode="barcode01",
                    body=body_content,
                    footer="All postive controls within threshold",
                    status='pass',
                    offcanvas_params=ocps),
                ICard(
                    alias="Sample2",
                    barcode="barcode02",
                    body="Test string",
                    status='warn',
                    offcanvas_params=ocps),
                ICard(
                    alias="Sample3",
                    barcode="barcode03",
                    body=body_content,
                    footer="NTC outside set thresholds.",
                    status='fail')
                    ])

    # This also adds to main_content, but provides a nice
    # container snippet as a starting context.
    with report.add_section('Alignment results', 'Results'):
        # This is the tabbed section with ezcharts!
        tabs = Tabs()
        with tabs.add_tab('Summary'):
            # Grids are snippets that provide responsive
            # layouts via css grid
            with Grid():
                EZChart(example_plot("line"))
                EZChart(example_plot("scatter"))
                EZChart(example_plot("bar"))
                EZChart(example_plot("histogram"))
                EZChart(example_plot("boxplot"))
                EZChart(example_plot("kdeplot"))

        with tabs.add_tab('Accuracy'):
            p("This is a mixed tab!")
            EZChart(example_plot())
        with tabs.add_tab('Depth'):
            p('Testing, testing, 1 2 3')

        # Dropdowns are nested one more level
        with tabs.add_dropdown_menu('Bar charts', change_header=False):
            with tabs.add_dropdown_tab('Simple'):
                # the simplest barplot
                plot = ezc.barplot(
                    data=example_df, x='year', y='sales'
                )
                EZChart(plot)
            with tabs.add_dropdown_tab('Simple - single colour'):
                # set color=grey for a uniform colouring
                plot = ezc.barplot(
                    data=example_df, x='year', y='sales', color='grey'
                )
                EZChart(plot)
            with tabs.add_dropdown_tab('Simple - additional styles'):
                # set margin to auto for horizontally centre plot
                plot = ezc.barplot(
                    data=example_df, x='year', y='sales'
                )
                EZChart(
                    plot, height="500px", width="500px",
                    additional_styles={"margin": "0 auto"})
            with tabs.add_dropdown_tab('Simple - single colour, ignore stacking'):
                # set color=grey for a uniform colouring
                # try setting also dodge=False, to check it doesn't break
                plot = ezc.barplot(
                    data=example_df, x='year', y='sales', color='grey', dodge=False
                )
                EZChart(plot)
            with tabs.add_dropdown_tab('Grouped'):
                # set dodge=True for a grouped barplot
                plot = ezc.barplot(
                    data=example_df, x='year', y='sales', hue='product', dodge=True
                )
                EZChart(plot)
            with tabs.add_dropdown_tab('Stacked'):
                # set dodge=False for a stacked barplot
                plot = ezc.barplot(
                    data=example_df, x='year', y='sales', hue='product', dodge=False
                )
                EZChart(plot)
            with tabs.add_dropdown_tab('Nested'):
                # set nested_x=True for a nested barplot
                plot = ezc.barplot(
                    data=example_df, x='year', y='sales', hue='product', nested_x=True
                )
                EZChart(plot)
        with tabs.add_dropdown_menu('Boxplots', change_header=False):
            with tabs.add_dropdown_tab('Single boxplot'):
                # use a 1D array of values
                plot = ezc.boxplot(
                    data=example_df['sales'], y='sales'
                )
                EZChart(plot)
            with tabs.add_dropdown_tab('Cycle colours'):
                boxplot_df = pd.DataFrame(
                    np.random.random((10, 15)),
                    columns=[f"var{i}" for i in range(1, 16)]
                )
                boxplot_df = boxplot_df.melt()
                boxplot_df.columns = ["variable", 'value']
                plot = ezc.boxplot(
                    data=boxplot_df, x='variable', y='value'
                )
                EZChart(plot)
        with tabs.add_tab('Empty plot'):
            # Force fail in plotting
            EZChart(empty_plot())

    with report.add_section('Nextclade results', 'Nextclade', True):
        NextClade(nxt_json)

    with report.add_section('Heatmap', 'Heatmap'):
        EZChart(example_plot("heatmap"))

    with report.add_section('Human Genome', 'Genome'):
        EZChart(
            ideogram(blocks='cytobands'), height="800px")

    with report.add_section('Human karyotype heatmap', 'Karyomap'):
        vals = pd.read_csv(
            resource_filename('ezcharts', "data/test/karyomap_vals.tsv.gz"), sep='\t')
        faidx = fasta_idx(resource_filename('ezcharts', "data/test/ref.fa.fai"))
        EZChart(karyomap(
            vals, 'chr', 'pos', 'values',
            stats='count',
            ref_lengths=faidx,
            order=HSA_CHROMOSOME_ORDER))

    with report.add_section('Sunburst', 'Sunburst'):
        lineages = [{'name': 'Bacteria', 'value': 600, 'children': [
            {'name': 'Firmicutes', 'value': 600, 'children': [
                {'name': 'Bacilli', 'value': 600, 'children': [
                    {'name': 'Bacillales', 'value': 600, 'children': [
                        {'name': 'Bacillaceae', 'value': 500, 'children': [
                            {'name': 'Bacillus', 'value': 500, 'children': [
                                {'name': 'Bacillus subtilis', 'value': 250},
                                {'name': 'Bacillus aquiflavi', 'value': 250}]}]},
                        {'name': 'Staphylococcaceae', 'value': 100, 'children': [
                            {'name': 'Staphylococcus', 'value': 100, 'children': [
                                {'name': 'Staphylococcus saccharolyticus',
                                    'value': 100}]}]}]}]}]}]}]

        EZChart(ezc.sunburst(
            lineages, label_rotate="tangential", label_minAngle=100))

    with report.add_section('Table', 'Table'):
        tabs = Tabs()
        with tabs.add_tab('Table'):
            df = pd.DataFrame(np.random.random((4, 4))) * 10
            df.columns = pd.MultiIndex.from_product(
                [['sample1', 'sample2'], ['mapped', 'unmapped']])
            df['chr'] = [1, 2, 3, 4]
            df = df.set_index('chr', drop=True)
            DataTable.from_pandas(df, use_index=True)
        with tabs.add_tab('Export'):
            df_simple = pd.DataFrame(np.random.random((4, 2))) * 10
            df_simple.columns = ['sample1', 'sample2']
            DataTable.from_pandas(df_simple, export=True, file_name='samples')

    with report.add_section('Sankey plot', 'Sankey'):
        sankey_json = resource_filename('ezcharts', "data/test/sankey.json")
        with open(sankey_json, 'r') as sfh:
            sankey_dict = json.load(sfh)
            ezc.metagenomics_sankey(sankey_dict)

    with report.add_section('Plasmid', 'Plasmid'):
        plannotate_json = resource_filename(
            'ezcharts', "data/test/seqviz/plannotate.json")
        fasta = resource_filename(
            'ezcharts', "data/test/seqviz/barcode01_q10.final.fasta")
        ezc.seqviz(plannotate_json, fasta, "sample_1")

    with report.add_section('Multiple sequence alignment', 'MSA'):
        msa_file = resource_filename('ezcharts', "data/test/msa/HIGD2A.fa")
        tabs = Tabs()
        with tabs.add_tab('Full MSA'):
            ezc.msa(msa_file, color_scheme="Blossom", identity=80)
        with tabs.add_tab('Partial MSA'):
            ezc.msa(msa_file, identity=50, start=30, end=80)

    dataset_examples = {
        'fastcat': load_stats(resource_filename(
            'ezcharts',
            "data/test/fastcat/f1.tsv.gz")),
        'bamstats': load_stats(resource_filename(
            'ezcharts',
            "data/test/bamstats/bamstats.readstats.tsv.gz")),
        'flagstat': load_bamstats_flagstat(resource_filename(
            'ezcharts', "data/test/bamstats.flagstat.tsv")),
        'modkit summary': load_modkit_summary(resource_filename(
            'ezcharts', "data/test/test_modkit_summary.tsv")),
        'modkit bedMethyl': load_bedmethyl(resource_filename(
            'ezcharts', "data/test/test_modkit.bed.gz")),
        'DSS DML': load_dml(resource_filename(
            'ezcharts', "data/test/test_dml.tsv.gz")),
        'DSS DMR': load_dmr(resource_filename(
            'ezcharts', "data/test/test_dmr.tsv.gz")),
        'mosdepth summary': load_mosdepth_summary(resource_filename(
            'ezcharts', "data/test/test_mosdepth_summary.tsv")),
        'mosdepth regions': load_mosdepth_regions(resource_filename(
            'ezcharts', "data/test/test_mosdepth.bed.gz")),
        'fai index': fasta_idx(resource_filename(
            'ezcharts', "data/test/ref.fa.fai")),
    }
    with report.add_section('Data types', 'Data'):
        p(
            "The workflow comes with a range of data loaders, as shown in the",
            "tables below (10 rows max displayed).")
        tabs = Tabs()
        with tabs.add_dropdown_menu():
            for data_type in dataset_examples.keys():
                df = dataset_examples[data_type]
                with tabs.add_dropdown_tab(data_type):
                    if isinstance(df, tuple) or isinstance(df, tuple):
                        for d in df:
                            DataTable.from_pandas(d.head(10))
                    else:
                        DataTable.from_pandas(df.head(10))
    with report.add_section("Bokeh", "Bokeh"):
        plot = BokehPlot()
        plot._fig.circle(
            [1, 2, 3, 4, 5],
            [6, 7, 2, 4, 5],
            size=20,
            color="navy",
            alpha=0.5,
        )
        plot._fig.title = "Bokeh plot title"
        EZChart(plot)

    with report.add_section('Per Sample Read Counts', 'Read Counts'):
        PlotMetaData(
            resource_filename('ezcharts', "data/test/metadata.json"))

    with report.add_section('Number formatting', 'Number formatting'):
        p(
            "Numbers can be formatted with SI prefixes.")
        numbers = np.random.default_rng().uniform(0.1, 1, 3) \
            * [1000000, 10000000, 100000000000]
        df_si_format = pd.DataFrame({"number": numbers.astype(int)})
        df_si_format["formatted"] = df_si_format["number"].map(si_format)
        DataTable.from_pandas(df_si_format)

    with report.add_section(
            "QC Status", 'QC Status'):
        with open(client_fields_json, encoding='utf-8') as f:
            client_fields = json.load(f)
            pretty_client_fields = {}
            for key, value in client_fields.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                pretty_client_fields[key.capitalize()] = value
        tabs = Tabs()
        with tabs.add_tab('Everything is fine'):
            LeadSummary(
                workflow_version=WORKFLOW_VERSION,
                sample_alias="demo_sample",
                client_fields=pretty_client_fields,
                reference="path/to/reference",
                qc_status={"status": True, "scope": "QC status"},
                qc_criteria=[
                    {"status": True, "scope": "All acceptance criteria met"},
                ],
                other_data={"Basecaller": "basecaller model",
                            "Missing value 1": None,
                            "Missing value 2": None}
            )
        with tabs.add_tab('or not'):
            LeadSummary(
                workflow_version=WORKFLOW_VERSION,
                sample_alias="demo_sample",
                client_fields=pretty_client_fields,
                reference="path/to/reference",
                qc_status={"status": False, "scope": "QC status"},
                qc_criteria=[
                    {
                        "status": False,
                        "category": "Non host reads summary",
                        "scope": "Total reads",
                    },
                    {
                        "status": False,
                        "category": "Non host reads summary",
                        "scope": "Min QS",
                    },
                ],
                n_columns=1,
                other_data={"Basecaller": "basecaller model"},
            )
        with tabs.add_tab('no QC'):
            LeadSummary(
                workflow_version=WORKFLOW_VERSION,
                sample_alias="demo_sample",
                client_fields=pretty_client_fields,
                reference="path/to/reference",
                n_columns=3
            )
        with tabs.add_tab('No reason to alert'):
            WorkflowQCBanner(workflow_pass=True, solid=False)
        with tabs.add_tab('Alert'):
            WorkflowQCBanner(workflow_pass=False, solid=False)

    with report.add_section('Details', 'Details'):
        # Software and params table
        ConfigurationTable(
            {"minimap2": "2.28-r1122", "fastcat": "0.22.0"},
            {
                "wfversion": WORKFLOW_VERSION,
                "fastq": "/wf-example/test_data/fastq",
            },
            WORKFLOW_VERSION,
            sample_specific=True
        )
    logger.info('Reticulating splines')
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        "ezcharts demo",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--output", default="ezcharts_demo_report.html",
        help="Output HTML file.")
    return parser
