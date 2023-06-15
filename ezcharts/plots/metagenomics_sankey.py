"""Visualizing matrices of data."""
import json

from dominate.tags import div, main, script, style
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
            div(
                raw(
                    """
                    <ul>
                        <li>
                            <label for="sample-select">Select sample</label>
                            <select id="sample-select"></select>
                        </li>
                        <li>
                            <label for="rank-select">Select rank</label>
                            <select id="rank-select"></select>
                        </li>
                        <li>
                            <label for="cutoff-select">Select cutoff</label>
                            <select id="cutoff-select"></select>
                        </li>
                        <li>
                            <button onclick="zoomIn()">[+] Zoom in</button>
                        </li>
                        <li>
                            <button onclick="zoomOut()">[-] Zoom out</button>
                        </li>
                        <li>
                            <button onclick="resetZoom()">[ ] Reset zoom</button>
                        </li>
                    </ul>
                    """
                ),
                id="controls",
            )
        with div(id="visualisation"):
            # the two divs below will be populated by the script
            div(id="sankey-plot")
            div(id="tooltip")
            script(raw(sankey_data))
