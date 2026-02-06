from pathlib import Path
from unittest.mock import mock_open, patch

from analyze_dna.full_health_analysis import analyze_genome, generate_comprehensive_report


def test_analyze_genome(mock_genome_data, mock_pharmgkb_data):
    mock_comp_snps = {
        "rs123": {
            "gene": "TEST1",
            "category": "Methylation",
            "variants": {
                "AA": {"status": "bad", "desc": "Very bad", "magnitude": 4},
                "GG": {"status": "good", "desc": "Very good", "magnitude": 0},
            },
        }
    }

    with patch("analyze_dna.full_health_analysis.COMPREHENSIVE_SNPS", mock_comp_snps):
        results = analyze_genome(mock_genome_data, mock_pharmgkb_data)

        assert len(results["findings"]) == 1
        assert results["findings"][0]["rsid"] == "rs123"
        assert results["findings"][0]["status"] == "bad"
        assert results["summary"]["high_impact"] == 1
        assert len(results["pharmgkb_findings"]) == 1


def test_generate_comprehensive_report():
    results = {
        "summary": {
            "total_snps": 1000,
            "analyzed_snps": 10,
            "high_impact": 1,
            "moderate_impact": 2,
            "low_impact": 3,
        },
        "findings": [
            {
                "gene": "GENE1",
                "rsid": "rs1",
                "category": "Methylation",
                "genotype": "AA",
                "status": "bad",
                "magnitude": 4,
                "description": "Desc",
                "note": "",
            }
        ],
        "by_category": {
            "Methylation": [
                {
                    "gene": "GENE1",
                    "rsid": "rs1",
                    "category": "Methylation",
                    "genotype": "AA",
                    "status": "bad",
                    "magnitude": 4,
                    "description": "Desc",
                    "note": "",
                }
            ]
        },
        "pharmgkb_findings": [
            {
                "gene": "GENE1",
                "rsid": "rs1",
                "drugs": "DrugA",
                "genotype": "AA",
                "annotation": "High risk",
                "level": "1A",
                "category": "Toxicity",
            }
        ],
    }

    with patch("builtins.open", mock_open()) as mocked_file:
        generate_comprehensive_report(results, Path("dummy_report.md"))
        mocked_file.assert_called_once()
        # Verify some content was written
        handle = mocked_file()
        calls = [call[0][0] for call in handle.write.call_args_list]
        full_content = "".join(calls)
        assert "Complete Genetic Health Optimization Report" in full_content
        assert "Methylation" in full_content
        assert "DrugA" in full_content
