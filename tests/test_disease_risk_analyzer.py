import pytest
from unittest.mock import patch, mock_open
from scripts.disease_risk_analyzer import load_clinvar, classify_zygosity_impact

CLINVAR_CONTENT = "chrom\tpos\tsymbol\tref\talt\tclinical_significance\tclinical_significance_ordered\treview_status\tgold_stars\tall_traits\tinheritance_modes\thgvs_c\thgvs_p\tmolecular_consequence\tall_pmids\txrefs\tage_of_onset\tprevalence\tall_submitters\tlast_evaluated\n1\t100\tTEST1\tA\tG\tpathogenic\tpathogenic\tcriteria\t1\tDisease A\tAutosomal Dominant\t\t\t\t\t\t\t\t\t\n"


def test_classify_zygosity():
    # Homozygous
    f = {"is_homozygous": True, "is_heterozygous": False, "inheritance": ""}
    assert classify_zygosity_impact(f)[0] == "AFFECTED"

    # Heterozygous Dominant
    f = {"is_homozygous": False, "is_heterozygous": True, "inheritance": "Autosomal Dominant"}
    assert classify_zygosity_impact(f)[0] == "AFFECTED"

    # Heterozygous Recessive
    f = {"is_homozygous": False, "is_heterozygous": True, "inheritance": "Autosomal Recessive"}
    assert classify_zygosity_impact(f)[0] == "CARRIER"


def test_load_clinvar_matching(mock_genome_by_position):
    # User has rs123 at 1:100 with genotype "AA".
    # ClinVar has 1:100 Ref: A, Alt: G.
    # User is AA (Ref/Ref). Should NOT match.

    with patch("scripts.disease_risk_analyzer.ensure_clinvar"):  # Skip decompression in tests
        with patch("builtins.open", mock_open(read_data=CLINVAR_CONTENT)):
            findings, stats = load_clinvar(mock_genome_by_position)
            assert stats["matched"] == 1  # Matches position
            assert stats["pathogenic_matched"] == 0  # But no variant allele match (user is AA, var is G)

    # Now let's try a match. User is AG.
    mock_genome_het = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("scripts.disease_risk_analyzer.ensure_clinvar"):  # Skip decompression in tests
        with patch("builtins.open", mock_open(read_data=CLINVAR_CONTENT)):
            findings, stats = load_clinvar(mock_genome_het)
            assert stats["matched"] == 1
            assert stats["pathogenic_matched"] == 1
            assert len(findings["pathogenic"]) == 1
