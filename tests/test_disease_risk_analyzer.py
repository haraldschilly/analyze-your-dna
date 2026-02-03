from unittest.mock import mock_open, patch

from scripts.disease_risk_analyzer import (
    classify_zygosity_impact,
    generate_report,
    get_carrier_phenotype_notes,
    load_clinvar,
)

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

    # Heterozygous X-linked
    f = {"is_homozygous": False, "is_heterozygous": True, "inheritance": "X-linked"}
    assert classify_zygosity_impact(f)[0] == "CARRIER/AT_RISK"


def test_load_clinvar_matching(mock_genome_by_position):
    # User has rs123 at 1:100 with genotype "AA".
    # ClinVar has 1:100 Ref: A, Alt: G.
    # User is AA (Ref/Ref). Should NOT match.
    with patch("scripts.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=CLINVAR_CONTENT)):
            findings, stats = load_clinvar(mock_genome_by_position)
            assert stats["matched"] == 1
            assert stats["pathogenic_matched"] == 0

    # User is AG.
    mock_genome_het = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("scripts.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=CLINVAR_CONTENT)):
            findings, stats = load_clinvar(mock_genome_het)
            assert stats["pathogenic_matched"] == 1
            assert len(findings["pathogenic"]) == 1


def test_generate_report(mock_genome_data):
    findings = {
        "pathogenic": [
            {
                "rsid": "rs123",
                "gene": "TEST1",
                "chromosome": "1",
                "position": "100",
                "user_genotype": "AA",
                "ref": "G",
                "alt": "A",
                "is_homozygous": True,
                "is_heterozygous": False,
                "clinical_significance": "Pathogenic",
                "gold_stars": 2,
                "review_status": "criteria",
                "traits": "Disease A",
                "inheritance": "Autosomal Dominant",
                "hgvs_p": "",
                "hgvs_c": "",
                "molecular_consequence": "",
                "pmids": "",
                "xrefs": "",
                "age_of_onset": "",
                "prevalence": "",
            }
        ],
        "likely_pathogenic": [],
        "risk_factor": [],
        "drug_response": [],
        "protective": [],
        "other_significant": [],
        "uncertain_but_notable": [],
    }
    stats = {"total_clinvar": 100, "matched": 10, "pathogenic_matched": 1, "likely_pathogenic_matched": 0}

    with patch("builtins.open", mock_open()) as mocked_file:
        report = generate_report(findings, stats, mock_genome_data)
        assert "Exhaustive Disease Risk Report" in report
        assert "TEST1" in report
        mocked_file.assert_called_once()


def test_carrier_notes():
    # CFTR note mentions lung function
    assert "lung function" in get_carrier_phenotype_notes("CFTR", "Cystic Fibrosis")
    # Default note mentions respiratory risk (wait, let me check default)
    assert "reproductive risk" in get_carrier_phenotype_notes("Unknown", "Unknown")
