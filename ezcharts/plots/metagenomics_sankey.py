"""Visualizing matrices of data."""
import json

from dominate.tags import button, div, label, li, main, script, select, style, ul
from dominate.util import raw

from ezcharts.layout.resource import ScriptResource, StyleResource


__all__ = ["metagenomics_sankey"]


def metagenomics_sankey(data):
    """Create a Sankey plot for taxonomic counts.

    :param data (dict): Dictionary with input data.

    Each node in the dict should contain values called `rank`, `count`, and `children`.

    example:
        {"Bacteria": {
            "rank": "superkingdom", "count": 3000, "children": { "Firmicutes": {...
    """
    # get relevant static assets
    sankey_D3_js = ScriptResource("metagenomics-sankey-util.js", tag=script)
    sankey_js = ScriptResource("metagenomics-sankey.js")
    sankey_css = StyleResource("metagenomics-sankey.css", tag=style)

    # add the D3 scripts
    sankey_D3_js()
    # load the actual sankey JS and insert the data
    insert = json.dumps(data).replace('"', '"')
    with open(sankey_js.data_file) as sankey_code_js:
        sankey_js = sankey_code_js.read()
    sankey_data = sankey_js.replace("replace_me", insert.replace('"', '\\"'))

    # create the plot
    with div(className="container"):
        # load sankey style
        sankey_css()

        with main(className="metagenomics-sankey"):
            with div(id="controls-sankey"):
                with ul():
                    li(
                        label("Select sample", fr="sample-select"),
                        select(id="sample-select")
                    )
                    li(
                        label("Select rank", fr="rank-select"),
                        select(id="rank-select")
                    )
                    li(
                        label("Select cutoff", fr="cutoff-select"),
                        select(id="cutoff-select")
                    )
                    with li():
                        with div(cls="dropdown"):
                            button("Options", cls="dropbtn")
                            with div(cls="dropdown-content"):
                                button("[+] Zoom in", onclick="zoomIn()")
                                button("[-] Zoom out", onclick="zoomOut()")
                                button("[ ] Reset zoom", onclick="resetZoom()")
                                button("Download", onclick="svgAsXML()")
            with div(id="visualisation"):
                # the two divs below will be populated by the script
                div(id="sankey-plot")
                div(id="tooltip")
                script(raw(sankey_data))
