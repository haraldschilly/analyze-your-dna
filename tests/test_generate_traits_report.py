from pathlib import Path
from unittest.mock import mock_open, patch

from analyze_dna.generate_traits_report import (
    analyze_traits_genome,
    check_genotype_match,
    complement_genotype,
    derive_blood_type,
    generate_traits_report,
    predict_eye_color_mlr,
)


def test_complement_genotype():
    assert complement_genotype("AA") == "TT"
    assert complement_genotype("CG") == "GC"
    assert complement_genotype("DI") == "DI"


def test_check_genotype_match():
    expected = {"AA": "info"}
    assert check_genotype_match("AA", expected) == ("AA", "info")
    assert check_genotype_match("TT", expected) == ("AA", "info")  # complement
    assert check_genotype_match("--", expected) == (None, None)


def test_predict_eye_color_mlr():
    # Test with critical SNP missing
    assert predict_eye_color_mlr({})["prediction"] == "Inconclusive"

    # Test with critical SNP present
    genome = {"rs12913832": "GG"}  # Homozygous G for HERC2 -> Blue
    result = predict_eye_color_mlr(genome)
    assert result["prediction"] != "Inconclusive"


def test_derive_blood_type():
    # Type O
    genome_o = {"rs8176719": "DD", "rs8176746": "GG"}
    assert derive_blood_type(genome_o)["blood_type"] == "O"

    # Type A
    genome_a = {"rs8176719": "II", "rs8176746": "GG"}
    assert derive_blood_type(genome_a)["blood_type"] == "A"

    # Type B
    genome_b = {"rs8176719": "II", "rs8176746": "TT"}
    assert derive_blood_type(genome_b)["blood_type"] == "B"


def test_analyze_traits_genome():
    mock_traits = {
        "rs123": {
            "gene": "TEST",
            "category": "Eye Color",
            "variants": {"AA": {"status": "blue", "desc": "Blue", "magnitude": 1}},
        }
    }
    with patch("analyze_dna.generate_traits_report.TRAITS_SNPS", mock_traits):
        results = analyze_traits_genome({"rs123": "AA"})
        assert results["summary"]["analyzed_traits"] == 1
        assert len(results["findings"]) == 1


def test_generate_traits_report():
    results = {
        "summary": {"total_snps": 100, "analyzed_traits": 5},
        "eye_color_mlr": {
            "prediction": "Blue",
            "confidence": 0.9,
            "probabilities": {"Blue": 0.9, "Intermediate": 0.05, "Brown": 0.05},
            "contributions": [],
            "reason": "",
        },
        "blood_type": {"blood_type": "O", "o_status": "DD", "ab_status": "GG", "reason": "reason"},
        "by_category": {},
        "findings": [],
        "mc1r_red_hair_score": 0,
    }
    with patch("builtins.open", mock_open()) as mocked_file:
        generate_traits_report(results, "John", Path("dummy.md"))
        mocked_file.assert_called_once()
