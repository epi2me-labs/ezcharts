"""A temporary example report."""
import os

from dominate.tags import h4, html, p

from ezcharts import Plot
from ezcharts.layout.components.document import (
    report_body, report_head, scriptd, styled)
from ezcharts.layout.components.footer import report_footer
from ezcharts.layout.components.grid import report_grid
from ezcharts.layout.components.header import (
    report_header, report_header_link)
from ezcharts.layout.components.section import report_section
from ezcharts.layout.components.summary import (
    report_summary, report_summary_badge)
from ezcharts.layout.components.table import (
    params_table, version_table)
from ezcharts.layout.components.tabs import (
    report_tab_button, report_tab_container, report_tabs)
from ezcharts.layout.ezchart import ezchart
from ezcharts.layout.utils import (
    inline, transpile, write_report)


# Setup simple globals
WORKFLOW_NAME = 'wf-template'
REPORT_TITLE = f'{WORKFLOW_NAME}-report'

# Dir!
path = os.path.abspath(__file__)
path_dir = os.path.dirname(path)
assets_dir = f'{path_dir}/assets'
vendor_dir = f'{assets_dir}/vendor'


# Good location to do prepare plots
def example_plot(style="line"):
    """Example plot."""
    df = pd.DataFrame({
        # as laid out in echarts docs for a dataset
        'product': [
            'Matcha Latte', 'Milk Tea', 'Cheese Cocoa', 'Walnut Brownie'],
        '2015': [43.3, 83.1, 86.4, 72.4],
        '2016': [85.8, 73.4, 65.2, 53.9],
        '2017': [93.7, 55.1, 82.5, 39.1]
    })
    # how we'd likely normally have it
    df = df.melt(
        id_vars=['product'], value_vars=['2015', '2016', '2017'],
        var_name='year', value_name='sales')
    if style == "line":
        p = ezc.lineplot(data=df, x='year', y='sales', hue='product')
    elif style == "scatter":
        p = ezc.scatterplot(data=df, x='year', y='sales', hue='product')
    else:
        raise ValueError("Unknown plot style")
    return p


# Declaritively create report document
document = html()
with document:

    # Adds the generic meta tags for us!
    with report_head(report_title=REPORT_TITLE):
        # Scripts and styles to preload
        scriptd(inline(f'{vendor_dir}/simple-datatables/simple-datatables.js'))
        styled(inline(f'{vendor_dir}/simple-datatables/simple-datatables.css'))
        scriptd(inline(f'{vendor_dir}/echarts.min.js'))
        styled(transpile(f'{assets_dir}/epi2melabs.scss'))

    # Enables scroll spy globals for us!
    with report_body():

        # This is the top header with scrollspy
        # We will be passing in an inlined svg element soon not a path!
        _header = report_header(logo=f'{assets_dir}/logo.svg')
        with _header.links:
            report_header_link(href='#alignment-results', title='Results')
            report_header_link(href='#software-versions', title='Versions')
            report_header_link(href='#workflow-parameters', title='Parameters')

        # This is the first banner with badges
        summary = report_summary('Summary', REPORT_TITLE, 'wf-template')
        with summary.badges:
            report_summary_badge("Research use only")
            report_summary_badge("29 July, 2022",
                bg_colour_class="bg-secondary")
            report_summary_badge("Revision: sha149529e3",
                bg_colour_class="bg-primary")

        # This is the tabbed section with ezcharts!
        with report_section(id="alignment-results"):
            h4('Alignment results')
            tabs = report_tabs()

            # Add the tab links / buttons
            with tabs.buttons:
                report_tab_button('Summary', active=True)
                report_tab_button('Accuracy')
                report_tab_button('Depth')

            # Add the tab contents
            with tabs.containers:
                with report_tab_container('Summary', active=True):
                    # A grid of plots!?
                    with report_grid():
                        # Take an ezchart plot and render it
                        ezchart(example_plot(style="line"))
                        ezchart(example_plot(style="scatter"))
                with report_tab_container('Accuracy'):
                    ezchart(example_plot("line"))
                with report_tab_container('Depth'):
                    p('Testing, testing, 1 2 3')

        # These are the tables using simple-datatables!
        with report_section(id="software-versions"):
            h4('Software versions')
            version_table(f'{path_dir}/test_data/versions.txt')

        with report_section(id="workflow-parameters"):
            h4('Workflow parameters')
            params_table(f'{path_dir}/test_data/params.json')

        # Generic footer
        report_footer()

        # Post init scripts
        scriptd(inline(f'{assets_dir}/tabs_ezcharts.js'))
        scriptd(inline(f'{vendor_dir}/bootstrap-5.0.2/js/bootstrap.bundle.min.js'))

write_report(f'{REPORT_TITLE}.html', document)
