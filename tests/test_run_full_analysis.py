from pathlib import Path
from unittest.mock import mock_open, patch

from analyze_dna.run_full_analysis import analyze_lifestyle_health, classify_zygosity, generate_actionable_protocol


def test_analyze_lifestyle_health(mock_genome_data, mock_pharmgkb_data):
    mock_comp_snps = {
        "rs123": {
            "gene": "TEST1",
            "category": "Methylation",
            "variants": {"AA": {"status": "bad", "desc": "Very bad", "magnitude": 4}},
        }
    }
    with patch("analyze_dna.run_full_analysis.COMPREHENSIVE_SNPS", mock_comp_snps):
        results = analyze_lifestyle_health(mock_genome_data, mock_pharmgkb_data)
        assert results["summary"]["high_impact"] == 1
        assert len(results["findings"]) == 1


def test_classify_zygosity():
    f = {"inheritance": "Autosomal Recessive", "is_homozygous": False, "is_heterozygous": True}
    assert classify_zygosity(f)[0] == "CARRIER"

    f = {"inheritance": "Autosomal Dominant", "is_homozygous": False, "is_heterozygous": True}
    assert classify_zygosity(f)[0] == "AFFECTED"


def test_generate_actionable_protocol():
    health_results = {
        "findings": [{"gene": "MTHFR", "magnitude": 2, "category": "Methylation", "description": "D"}],
        "pharmgkb_findings": [],
    }
    disease_findings = {"pathogenic": [], "risk_factor": [], "protective": []}

    with patch("builtins.open", mock_open()) as mocked_file:
        generate_actionable_protocol(health_results, disease_findings, Path("dummy.md"))
        mocked_file.assert_called_once()
        handle = mocked_file()
        calls = [call[0][0] for call in handle.write.call_args_list]
        full_content = "".join(calls)
        assert "Methylfolate" in full_content
