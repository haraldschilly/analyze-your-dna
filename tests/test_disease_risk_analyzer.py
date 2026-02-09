from unittest.mock import mock_open, patch

from analyze_dna.disease_risk_analyzer import (
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


def test_classify_zygosity_heterozygous_unspecified():
    """Heterozygous with unspecified inheritance should be HETEROZYGOUS."""
    f = {"is_homozygous": False, "is_heterozygous": True, "inheritance": ""}
    assert classify_zygosity_impact(f)[0] == "HETEROZYGOUS"


def test_classify_zygosity_unknown():
    """Neither homo nor hetero should be UNKNOWN."""
    f = {"is_homozygous": False, "is_heterozygous": False, "inheritance": ""}
    assert classify_zygosity_impact(f)[0] == "UNKNOWN"


def test_load_clinvar_matching(mock_genome_by_position):
    # User has rs123 at 1:100 with genotype "AA".
    # ClinVar has 1:100 Ref: A, Alt: G.
    # User is AA (Ref/Ref). Should NOT match.
    with patch("analyze_dna.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=CLINVAR_CONTENT)):
            findings, stats = load_clinvar(mock_genome_by_position)
            assert stats["matched"] == 1
            assert stats["pathogenic_matched"] == 0

    # User is AG.
    mock_genome_het = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("analyze_dna.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=CLINVAR_CONTENT)):
            findings, stats = load_clinvar(mock_genome_het)
            assert stats["pathogenic_matched"] == 1
            assert len(findings["pathogenic"]) == 1


def test_load_clinvar_indel_filtering():
    """Indels (ref/alt length != 1) should be skipped."""
    clinvar_with_indel = "chrom\tpos\tsymbol\tref\talt\tclinical_significance\tclinical_significance_ordered\treview_status\tgold_stars\tall_traits\tinheritance_modes\thgvs_c\thgvs_p\tmolecular_consequence\tall_pmids\txrefs\tage_of_onset\tprevalence\tall_submitters\tlast_evaluated\n1\t100\tTEST1\tAG\tA\tpathogenic\tpathogenic\tcriteria\t1\tDisease A\tAutosomal Dominant\t\t\t\t\t\t\t\t\t\n"
    mock_genome = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("analyze_dna.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=clinvar_with_indel)):
            findings, stats = load_clinvar(mock_genome)
            # Should match position but skip the indel, so no pathogenic findings
            assert stats["pathogenic_matched"] == 0


def test_load_clinvar_likely_pathogenic():
    """Likely pathogenic variants should be categorized correctly."""
    clinvar_lp = "chrom\tpos\tsymbol\tref\talt\tclinical_significance\tclinical_significance_ordered\treview_status\tgold_stars\tall_traits\tinheritance_modes\thgvs_c\thgvs_p\tmolecular_consequence\tall_pmids\txrefs\tage_of_onset\tprevalence\tall_submitters\tlast_evaluated\n1\t100\tTEST1\tA\tG\tlikely pathogenic\tlikely pathogenic\tcriteria\t1\tDisease A\tAutosomal Dominant\t\t\t\t\t\t\t\t\t\n"
    mock_genome = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("analyze_dna.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=clinvar_lp)):
            findings, stats = load_clinvar(mock_genome)
            assert len(findings["likely_pathogenic"]) == 1


def test_load_clinvar_risk_factor():
    """Risk factor variants should be categorized correctly."""
    clinvar_rf = "chrom\tpos\tsymbol\tref\talt\tclinical_significance\tclinical_significance_ordered\treview_status\tgold_stars\tall_traits\tinheritance_modes\thgvs_c\thgvs_p\tmolecular_consequence\tall_pmids\txrefs\tage_of_onset\tprevalence\tall_submitters\tlast_evaluated\n1\t100\tTEST1\tA\tG\trisk factor\trisk factor\tcriteria\t1\tDisease A\t\t\t\t\t\t\t\t\t\t\n"
    mock_genome = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("analyze_dna.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=clinvar_rf)):
            findings, stats = load_clinvar(mock_genome)
            assert len(findings["risk_factor"]) == 1


def test_load_clinvar_drug_response():
    """Drug response variants should be categorized correctly."""
    clinvar_dr = "chrom\tpos\tsymbol\tref\talt\tclinical_significance\tclinical_significance_ordered\treview_status\tgold_stars\tall_traits\tinheritance_modes\thgvs_c\thgvs_p\tmolecular_consequence\tall_pmids\txrefs\tage_of_onset\tprevalence\tall_submitters\tlast_evaluated\n1\t100\tTEST1\tA\tG\tdrug response\tdrug response\tcriteria\t1\tDrug A\t\t\t\t\t\t\t\t\t\t\n"
    mock_genome = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("analyze_dna.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=clinvar_dr)):
            findings, stats = load_clinvar(mock_genome)
            assert len(findings["drug_response"]) == 1


def test_load_clinvar_protective():
    """Protective variants should be categorized correctly."""
    clinvar_prot = "chrom\tpos\tsymbol\tref\talt\tclinical_significance\tclinical_significance_ordered\treview_status\tgold_stars\tall_traits\tinheritance_modes\thgvs_c\thgvs_p\tmolecular_consequence\tall_pmids\txrefs\tage_of_onset\tprevalence\tall_submitters\tlast_evaluated\n1\t100\tTEST1\tA\tG\tprotective\tprotective\tcriteria\t1\tDisease A\t\t\t\t\t\t\t\t\t\t\n"
    mock_genome = {"1:100": {"rsid": "rs123", "genotype": "AG"}}
    with patch("analyze_dna.disease_risk_analyzer.ensure_clinvar"):
        with patch("builtins.open", mock_open(read_data=clinvar_prot)):
            findings, stats = load_clinvar(mock_genome)
            assert len(findings["protective"]) == 1


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


def test_generate_report_with_carrier():
    """Test report with carrier findings generates carrier section."""
    findings = {
        "pathogenic": [
            {
                "rsid": "rs123",
                "gene": "CFTR",
                "chromosome": "7",
                "position": "117559590",
                "user_genotype": "AG",
                "ref": "A",
                "alt": "G",
                "is_homozygous": False,
                "is_heterozygous": True,
                "clinical_significance": "Pathogenic",
                "gold_stars": 3,
                "review_status": "reviewed",
                "traits": "Cystic Fibrosis",
                "inheritance": "Autosomal Recessive",
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
    genome = {"rs123": {"chromosome": "7", "position": "117559590", "genotype": "AG"}}

    with patch("builtins.open", mock_open()):
        report = generate_report(findings, stats, genome)
        assert "Carrier" in report
        assert "CFTR" in report


def test_generate_report_with_risk_factors():
    """Test report with risk factor findings."""
    findings = {
        "pathogenic": [],
        "likely_pathogenic": [],
        "risk_factor": [
            {
                "rsid": "rs100",
                "gene": "TESTGENE",
                "chromosome": "1",
                "position": "500",
                "user_genotype": "AG",
                "ref": "A",
                "alt": "G",
                "is_homozygous": False,
                "is_heterozygous": True,
                "clinical_significance": "risk factor",
                "gold_stars": 2,
                "review_status": "criteria",
                "traits": "Susceptibility to Disease B",
                "inheritance": "",
                "hgvs_p": "",
                "hgvs_c": "",
                "molecular_consequence": "",
                "pmids": "",
                "xrefs": "",
                "age_of_onset": "",
                "prevalence": "",
            }
        ],
        "drug_response": [],
        "protective": [],
        "other_significant": [],
        "uncertain_but_notable": [],
    }
    stats = {"total_clinvar": 100, "matched": 5, "pathogenic_matched": 0, "likely_pathogenic_matched": 0}
    genome = {"rs100": {"chromosome": "1", "position": "500", "genotype": "AG"}}

    with patch("builtins.open", mock_open()):
        report = generate_report(findings, stats, genome)
        assert "Risk Factor" in report or "risk factor" in report.lower()
        assert "TESTGENE" in report


def test_generate_report_empty():
    """Test report with no findings at all."""
    findings = {
        "pathogenic": [],
        "likely_pathogenic": [],
        "risk_factor": [],
        "drug_response": [],
        "protective": [],
        "other_significant": [],
        "uncertain_but_notable": [],
    }
    stats = {"total_clinvar": 100, "matched": 50, "pathogenic_matched": 0, "likely_pathogenic_matched": 0}
    genome = {"rs1": {"chromosome": "1", "position": "1", "genotype": "AA"}}

    with patch("builtins.open", mock_open()):
        report = generate_report(findings, stats, genome)
        assert "Exhaustive Disease Risk Report" in report
        # Should still have disclaimer
        assert "Disclaimer" in report or "disclaimer" in report.lower()


def test_carrier_notes():
    # CFTR note mentions lung function
    assert "lung function" in get_carrier_phenotype_notes("CFTR", "Cystic Fibrosis")
    # Default note mentions reproductive risk
    assert "reproductive risk" in get_carrier_phenotype_notes("Unknown", "Unknown")


def test_carrier_notes_all_genes():
    """Test carrier notes for every known gene in the carrier_effects dict."""
    known_genes = ["CFTR", "HBB", "SERPINA1", "GBA", "HFE", "HEXA", "SMN1", "PAH"]
    for gene in known_genes:
        notes = get_carrier_phenotype_notes(gene, "Some Condition")
        assert "Recommended" in notes, f"Gene {gene} should have recommendations"
        assert len(notes) > 20, f"Gene {gene} notes too short"


def test_carrier_notes_case_insensitive():
    """Gene lookup should be case-insensitive."""
    result = get_carrier_phenotype_notes("cftr", "Cystic Fibrosis")
    assert "lung function" in result


def test_carrier_notes_unknown_gene():
    """Unknown gene should return generic carrier notes."""
    result = get_carrier_phenotype_notes("BRCA1", "Breast Cancer")
    assert "reproductive risk" in result
    assert "genetic counseling" in result.lower()
