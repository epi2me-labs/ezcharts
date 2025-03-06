"""Make an multiple sequence alignment image."""
import base64
import os

from Bio import AlignIO
from dominate.tags import img, p
from pymsaviz import MsaViz


__all__ = ["msa"]

COLOR_SCHEMES = [
    'Clustal',
    'Zappo',
    'Taylor',
    'Flower',
    'Blossom',
    'Sunset',
    'Ocean',
    'Hydrophobicity',
    'HelixPropensity',
    'StrandPropensity',
    'TurnPropensity',
    'BuriedIndex',
    'Nucleotide',
    'Purine/Pyrimidine',
    'Identity',
    'None'
]


def msa(
        msa_file,
        color='#0ebbb2',
        wrap_lengh=80,
        show_count=True,
        identity_color_min_thr=40,
        show_consensus=False,
        color_scheme="Identity",
        identity=50,
        start=0,
        end=None):
    """
    Make a nice multiple sequence alignment with pymsaviz.

    Args:
        msa_file (str): The path to the MSA file in AFA (Aligned FASTA) format.
        color (str, optional): The color to use for the alignment.
        Defaults to '#0ebbb2'.
        wrap_lengh (int, optional): The maximum length of each line in the
        alignment. Defaults to 80.
        show_count (bool, optional): Whether to show the count of each residue
        in the alignment. Defaults to True.
        show_consensus (bool, optional): Whether to show the consensus
        sequence in the alignment. Defaults to False.
        color_scheme (str, optional): The color scheme to use for the
        alignment. Defaults to "Identity".
        identity (int, optional): The minimum identity threshold for
        highlighting mismatches. Defaults to 50.
        start (int): The start position compliant with bed format. Defaults to 0
        end (int, optional): The end position compliant with bed format.
        If empty MSA will be start:len(MSA).

    Returns:
        str: The HTML code for displaying the generated alignment image.
    """
    # check MSA file exists
    if not os.path.exists(msa_file):
        return p("Unable to plot MSA. MSA file not found.")

    # check for records in the MSA file
    try:
        alignment = AlignIO.read(msa_file, "fasta")
        if len(alignment) == 0:
            return p("Unable to plot MSA. MSA file does not contain any records.")
    except (ValueError, FileNotFoundError):
        return p("Unable to plot MSA. Invalid FASTA file.")

    # check color scheme is allowed
    if color_scheme not in COLOR_SCHEMES:
        return p(f"Invalid color scheme. Choose from: {', '.join(COLOR_SCHEMES)}")

    mv = MsaViz(
        msa_file,
        wrap_length=wrap_lengh,
        show_count=show_count,
        show_consensus=show_consensus,
        color_scheme=color_scheme,
        start=start+1,  # Start is bed file 0-based, but MsaViz is 1-based
        end=end)

    pos_ident = []
    ident_list = mv._get_consensus_identity_list()

    # for each position get those with less than dev specified identity. Default is 50.
    for pos, ident in enumerate(ident_list, 1):
        if ident <= identity:
            pos_ident.append(pos)

    # add dots over mismatches
    mv.add_markers(
        pos_ident, marker="o", color="#c22932")

    # change to ONT colours
    mv.set_plot_params(
        identity_color=color, identity_color_min_thr=identity_color_min_thr)

    mv.savefig("msa.png")

    with open("msa.png", "rb") as image_file:
        data = base64.b64encode(image_file.read())

    return img(
        src=f"data:image/png;base64,{data.decode('utf-8')}",
        cls="img-fluid")
