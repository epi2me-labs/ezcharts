"""An ezcharts component for loading ClinVar annotated VCF files."""
import argparse
import os

from dominate.tags import a, span
from natsort import natsort_keygen
import pandas as pd
from pandas.api import types as pd_types
from pysam import VariantFile

from ezcharts.components.common import CLINVAR_BASE, NCBI_BASE
from ezcharts.components.reports.comp import ComponentReport
from ezcharts.layout.base import Snippet
from ezcharts.layout.snippets import DataTable, Tabs
from ezcharts.layout.util import isolate_context

# Categorical types
CATEGORICAL = pd_types.CategoricalDtype(ordered=True)


class ClinVarTable(Snippet):
    """Generate modified bases summary plots."""

    def __init__(self, theme='epi2melabs', **kwargs):
        """Create ClinVar data table.

        If multiple single-sample VCFs are provided, each will be
        displayed in a distinct tab.

        :param vcf_fn: A path to a single-sample vcf file annotated with ClinVar fields
            or a pandas DataFrame from load_clinvar_vcf
        :param benign: A boolean specifying whether to include the benign sites in
            the report
        :param all_sites: A boolean specifying whether to include the every sites in
            the report
        """
        super().__init__(styles=None, classes=None)

        with self:
            # Make table of clinvar sites
            if "vcf_fn" in kwargs:
                if isinstance(kwargs["vcf_fn"], pd.DataFrame):
                    clinvar_df = kwargs["vcf_fn"]
                else:
                    clinvar_df = load_clinvar_vcf(
                        kwargs["vcf_fn"],
                        benign=kwargs["benign"],
                        all_sites=kwargs["all_sites"])
                # Check that the file is not empty
                if clinvar_df.empty:
                    raise pd.errors.EmptyDataError('Input VCF is empty')
                # If one sample, save one plot
                if len(clinvar_df['Sample'].unique()) == 1:
                    # we only got a single sample --> no dropdown
                    DataTable.from_pandas(
                        clinvar_df, export=True, use_index=False)
                else:
                    # several samples --> use a dropdown menu
                    tabs = Tabs()
                    with tabs.add_dropdown_menu():
                        for sample_id, df_sample in clinvar_df.groupby('sample_name'):
                            with tabs.add_dropdown_tab(sample_id):
                                DataTable.from_pandas(
                                    df_sample, export=True, use_index=False)


# Function to load a single VCF file.
def load_vcf(vcf_fn, benign=False, all_sites=False):
    """Import a single vcf file."""
    # Start processing the data
    data = []
    columns = {
        'Sample': CATEGORICAL,
        "Chrom": CATEGORICAL,
        "Pos": int,
        "Gene(s)": CATEGORICAL,
        "ClinVar": CATEGORICAL,
        "Significance": CATEGORICAL,
        "Type": CATEGORICAL,
        "Consequence": CATEGORICAL,
        "HGVSc": CATEGORICAL,
        "HGVSp": CATEGORICAL,
    }

    # Load the VCF. If empty, return empty DF.
    try:
        vcf_file = VariantFile(vcf_fn)
    except ValueError:
        return pd.DataFrame(columns=columns).astype(columns)

    # Get sample name
    if len(vcf_file.header.samples) != 1:
        raise ValueError(f'File {vcf_fn} has more than one sample')
    else:
        sample_name = vcf_file.header.samples[0]

    # Process each record in the VCF file
    for variant in vcf_file.fetch():
        # First thing first, we check if the site has an alternative allele
        # and if not we skip it.
        if not variant.alts:
            continue

        # clinvar significance
        if 'CLNSIG' not in variant.info:
            # if absent and benign are requested, then set to "Not provided"
            if all_sites:
                significance = 'Not provided'
            # otherwise skip
            else:
                continue
        # if present, process appropriately
        else:
            significance = ", ".join(variant.info['CLNSIG'])

        # If the site is benign, ignore it (unless otherwise specified)
        if 'benign' in significance.lower() and not benign and not all_sites:
            continue
        else:
            # NCBI gene URL
            try:
                all_ncbi_urls = []
                clinvar_gene_string = variant.info['GENEINFO']
                # CW-2783: If there is a tuple, each element will be split
                # independently and added to the list. Duplicated entries are
                # dropped using a tuple/set/tuple conversion.
                if type(clinvar_gene_string) is tuple:
                    all_genes = list(
                        set([
                            i for string in clinvar_gene_string
                            for i in string.split('|')
                        ]))
                else:
                    all_genes = clinvar_gene_string.split('|')

                for gene in all_genes:
                    gene_symbol, gene_id = gene.split(':')
                    with isolate_context():
                        ncbi_url = str(a(
                            gene_symbol,
                            href=f'{NCBI_BASE}{gene_id}'))
                        all_ncbi_urls.append(ncbi_url)
                ncbi_gene_url = ", ".join(all_ncbi_urls)
            except KeyError:
                ncbi_gene_url = "No affected genes found"

            # multiple ClinVar IDs possible, separated by ';'
            clinvar_url_list = []
            clinvar_id = variant.id
            if not clinvar_id or clinvar_id == '.':
                clinvar_urls_for_report = '.'
            else:
                all_clinvar_ids = clinvar_id.split(';')
                for each_id in all_clinvar_ids:
                    with isolate_context():
                        clinvar_url = str(a(
                            each_id, href=f'{CLINVAR_BASE}{each_id}'))
                        clinvar_url_list.append(clinvar_url)
                clinvar_urls_for_report = ", ".join(clinvar_url_list)

            # tidy up significances
            significance = significance.replace("_", " ").replace(
                "|", ", ").capitalize()

            # tidy up variant types
            try:
                variant_type = variant.info['CLNVC']
                # CW-2783: There should be just one variant type, but in case multiple
                # alleles are present the variant types are combined in a
                # comma-separated list (duplicates are still removed via set).
                if type(variant_type) is tuple:
                    variant_type = [
                        vt.replace("_", " ").capitalize() for vt in set(variant_type)
                    ]
                    variant_type = ','.join([
                        'SNV' if v == 'Single nucleotide variant' else v
                        for v in variant_type
                    ])
                else:
                    variant_type = variant_type.replace("_", " ").capitalize()
                    if variant_type == 'Single nucleotide variant':
                        variant_type = 'SNV'
            except KeyError:
                # If not CLNVC, use variant type from pysam
                variant_type = variant.alleles_variant_types[1]

            # tidy up consequences
            consequences = []
            try:
                all_consequences = variant.info['MC']
                for each_conseq in all_consequences:
                    ontology, consequence = each_conseq.split('|')
                    consequence = consequence.replace("_", " ").capitalize()
                    consequence = consequence.replace(
                        " prime utr", "' UTR")
                    consequences.append(consequence)
                consequences = ", ".join(consequences)
            except KeyError:
                consequences = "No consequences found"

            # HGVS p. and c. come from the SnpEff ANN field, we will take the first
            # available 'NM_' number
            hgvsc = ""
            hgvsp = ""
            all_variant_info = variant.info['ANN']
            for each_variant in all_variant_info:
                fields = each_variant.split('|')
                # find the first NM (because there are some XM records present)
                if fields[6].startswith("NM"):
                    hgvsc = f"{fields[6]}:{fields[9]}"
                    hgvsp = fields[10] if fields[10] != "" else "-"
                    break
                # if there are only XMs then display the first one of those instead
                else:
                    hgvsc = f"{fields[6]}:{fields[9]}"
                    hgvsp = fields[10] if fields[10] != "" else "-"

        # Create record tuple
        record = (
            sample_name, variant.chrom, variant.pos, ncbi_gene_url,
            clinvar_urls_for_report, significance, variant_type,
            consequences, hgvsc, hgvsp
        )
        data.append(record)

    # Put together the dataframe
    df = pd.DataFrame(data, columns=columns)

    # Check if it is empty, and if so return a "No sites" line for the sample
    if df.empty:
        record = (
            sample_name, 'No sites', '', '', '',
            '', '', '', '', ''
        )
        return pd.DataFrame(data, columns=columns).astype(columns)

    # get unique list of all significances in the df
    sample_significances = df['Significance'].unique()

    # desired order of ClinVar significances
    significance_order = [
        "Pathogenic", "Pathogenic, low penetrance",
        "Likely pathogenic", "Likely pathogenic, low penetrance",
        "Uncertain significance", "Conflicting interpretations of pathogenicity",
        "Risk factor", "Established risk allele", "Likely risk allele",
        "Uncertain risk allele", "Association", "Confers sensitivity", "Affects",
        "Protective", "Association not found", "Drug response", "Other",
        "Not provided", "Benign"]

    """re-order variant significances found in the sample to the desired order
    also ensures there are no duplicate significances as this will cause a
    problem when setting 'Significance' to a categorical column later
    """
    reordered = [
        y for x in significance_order for y in sample_significances if y.startswith(x)]
    reordered_unique = sorted(set(reordered), key=reordered.index)

    # define custom sort for chromosomes
    def nat_sort_chromosome(col):
        if col.name == "Chrom":
            return col.apply(natsort_keygen())
        return col

    # sort the sample ClinVar results using the re-ordered significances
    df["Significance"] = pd.Categorical(
        df["Significance"], categories=reordered_unique)
    df.sort_values(
        by=["Significance", "Chrom", "Pos"], inplace=True, key=nat_sort_chromosome)

    return df.astype(columns)


# Load mod bedMethyl file
def load_clinvar_vcf(vcf_fn, benign=False, all_sites=False):
    """Convert ClinVar VCF to sorted df."""
    if os.path.isdir(vcf_fn):
        dfs = [
            load_vcf(f"{vcf_fn}/{i}", benign=benign, all_sites=all_sites)
            for i in os.listdir(vcf_fn)
            if i.endswith(('.vcf', '.vcf.gz', 'bcf'))]
    elif os.path.isfile(vcf_fn) and vcf_fn.endswith(('.vcf', '.vcf.gz', 'bcf')):
        dfs = [load_vcf(vcf_fn, benign=benign, all_sites=all_sites)]
    else:
        raise Exception(f'No valid input: {vcf_fn}')

    return pd.concat(dfs)


def format_clinvar_table(df):
    """Format ClinVar dataframe to add badges where required."""
    df_for_table = df.copy()
    # uncategorise the 'Significance' column so we can add badges
    df_for_table['Significance'] = df_for_table['Significance'].astype(
        df_for_table['Significance'].cat.categories.to_numpy().dtype)

    significance_badges = {
        "Pathogenic": "badge bg-danger",
        "Likely pathogenic": "badge bg-warning",
        "Uncertain": "badge bg-primary"
    }
    for idx, sig in df["Significance"].items():
        for significance, class_name in significance_badges.items():
            if sig.startswith(significance):
                df_for_table.loc[idx, "Significance"] = str(span(sig, cls=class_name))
                break
    return (df_for_table)


def main(args):
    """Entry point to demonstrate a ClinVar data table."""
    comp_title = 'ClinVar data'
    seq_sum = ClinVarTable(
        vcf_fn=args.vcf,
        benign=args.benign,
        all_sites=args.all_sites
        )
    report = ComponentReport(comp_title, seq_sum)
    report.write(args.output)


def argparser():
    """Argument parser for entrypoint."""
    parser = argparse.ArgumentParser(
        'ClinVar summary',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=False)
    parser.add_argument(
        "--vcf",
        default=None,
        required=True,
        help="Input VCF file.")
    parser.add_argument(
        "--benign",
        action='store_true',
        help="Report benign sites in the VCF file.")
    parser.add_argument(
        "--all_sites",
        action='store_true',
        help="Report all sites in the VCF file.")
    parser.add_argument(
        "--output",
        default="clinvar_report.html",
        help="Output HTML file.")
    return parser
