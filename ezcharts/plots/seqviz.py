"""Visualizing plasmids."""
import json
import os


from Bio import SeqIO
from dominate.tags import button, div, h6, input_, label, main, script
from dominate.util import raw

from ezcharts.layout.resource import VendorResource


__all__ = ["seqviz"]


def seqviz(plannotate_json, fasta, alias):
    """Visualize a plasmid using SeqViz."""
    if not os.path.exists(fasta):
        raise FileNotFoundError(f"{fasta} not found")

    if not os.path.exists(plannotate_json):
        raise FileNotFoundError(f"{plannotate_json} not found")

    records = list(SeqIO.parse(fasta, "fasta"))
    if len(records) != 1:
        raise ValueError(f"Expected 1 record in {fasta}, found {len(records)}")

    sequence = records[0].seq
    plannotate = json.load(open(plannotate_json))

    # features
    features = [
        dict(
            start=feature["Start Location"],
            end=feature["End Location"],
            name=feature["Feature"],
            direction=feature["Strand"]
         ) for feature in plannotate[alias]["features"]
    ]

    # primers { start: 33, end: 53, name: "LacZ Foward Primer", direction: 1 }
    primers = list()
    if 'primers' in plannotate[alias]:
        primers = [
            dict(
                start=primer["Start Location"],
                end=primer["End Location"],
                name=primer["Feature"],
                direction=primer["Strand"],
                color="#FAA887"
            ) for primer in plannotate[alias]["primers"]
        ]

    # place holder until we get the restriction enzymes from the plannotate json
    enzymes = list()
    if 'enzymes' in plannotate[alias]:
        enzymes = [enzyme['name'] for enzyme in plannotate[alias]["enzymes"]]

    # add the seqviz js
    seqviz_js = VendorResource("seqviz.min.js", tag=script)
    seqviz_js()

    with div(className="container"):
        with div(id="seqviz", cls="bg-light border p-4"):
            button(
                "Toggle controls",
                cls="btn btn-primary",
                type="button",
                onclick="showDiv()")

            with div(
                    cls="border p-4 my-3 bg-white",
                    style="display:none;",
                    id="controls"):
                h6("Search")
                input_(
                    placeholder="Search for a sequence...",
                    type="text",
                    cls="form-control mb-3",
                    value="",
                    id="seqviz_search")

                if len(enzymes) > 1:
                    h6("Restriction enzymes")
                    for count, enzyme in enumerate(enzymes):
                        input_(
                            type="checkbox",
                            id=f"enzyme{count}",
                            name="enzyme",
                            value=enzyme,
                            cls="",
                            onclick="seqviz_render()")

                        label(enzyme, cls="form-check-label", for_=f"enzyme{count}")

                    button(
                        "Select all",
                        type="button",
                        cls="btn btn-primary btn-sm",
                        onclick="toggle(true)")

                    button(
                        "Select none",
                        type="button",
                        cls="btn btn-primary btn-sm",
                        onclick="toggle(false)")

            div(id="seqviz_container")

        with main(className="seqviz_plasmid"):
            div(
                raw(f"""
                    <script>
                        seqviz_render()
                        document.getElementById(
                            "seqviz_search").addEventListener("keyup", seqviz_render);

                        // show our controls div
                        function showDiv() {{
                            var div = document.getElementById('controls');
                                if (div.style.display !== 'none') {{
                                    div.style.display = 'none';
                                }}
                                else {{
                                    div.style.display = 'block';
                                }}
                        }};

                        // get state of checkboxes
                        function toggle(state) {{
                            checkboxes = document.getElementsByName('enzyme');
                            for(var i=0, n=checkboxes.length;i<n;i++) {{
                                checkboxes[i].checked = state;
                            }}
                            seqviz_render()
                        }}

                        function seqviz_render() {{
                            var enzymes = []
                            var checkboxes = document.querySelectorAll(
                                'input[name=enzyme]:checked')
                            for (var i = 0; i < checkboxes.length; i++) {{
                                enzymes.push(checkboxes[i].value)
                            }}

                            search = {{
                                query: document.getElementById('seqviz_search').value,
                                mismatch: 0 }};

                            window.seqviz
                            .Viewer("seqviz_container", {{
                                name: "{alias}",
                                seq: "{sequence}",
                                annotations: {features},
                                primers: {primers},
                                enzymes: enzymes,
                                search: search,
                                style: {{ height: "500px", width: "100%" }},
                            }})
                            .render();
                        }}
                    </script>
                    """),
                id="controls",
            )
