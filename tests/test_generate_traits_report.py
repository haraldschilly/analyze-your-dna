from unittest.mock import patch

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


def test_check_genotype_match_reversed():
    """Test reversed genotype matching (AG vs GA)."""
    expected = {"AG": "info"}
    assert check_genotype_match("GA", expected) == ("AG", "info")


def test_check_genotype_match_complement_reversed():
    """Test complement + reversed matching."""
    # AC -> complement = TG -> not found, reverse of AC = CA -> not found,
    # complement(AC) = TG, reverse of TG = GT -> found!
    expected = {"GT": "info2"}
    assert check_genotype_match("AC", expected) == ("GT", "info2")


def test_check_genotype_match_no_match():
    """Test when no match is possible."""
    expected = {"AA": "info"}
    assert check_genotype_match("CG", expected) == (None, None)


def test_predict_eye_color_mlr():
    # Test with critical SNP missing
    assert predict_eye_color_mlr({})["prediction"] == "Inconclusive"

    # Test with critical SNP present
    genome = {"rs12913832": "GG"}  # Homozygous G for HERC2 -> Blue
    result = predict_eye_color_mlr(genome)
    assert result["prediction"] != "Inconclusive"


def test_predict_eye_color_mlr_blue():
    """Homozygous GG at HERC2 should predict blue with high confidence."""
    genome = {
        "rs12913832": "GG",  # HERC2 master switch -> strong blue
        "rs1800407": "AA",  # OCA2 lightening (A = light allele)
        "rs16891982": "GG",  # SLC45A2 light (G = derived/light in Europeans)
    }
    result = predict_eye_color_mlr(genome)
    assert result["prediction"] == "Blue"
    assert result["confidence"] > 0.70


def test_predict_eye_color_mlr_brown():
    """No light alleles should predict brown with high confidence.

    With negative intercepts and no light alleles contributing,
    the model correctly defaults to brown (~85%), matching the
    known heuristic: AA at HERC2 -> ~85% brown.
    """
    genome = {
        "rs12913832": "AA",  # HERC2 -> 0 G alleles (dark)
        "rs16891982": "CC",  # SLC45A2 -> 0 G alleles (dark/ancestral)
        "rs1393350": "GG",  # TYR -> 0 A alleles (dark/high activity)
    }
    result = predict_eye_color_mlr(genome)
    assert result["prediction"] == "Brown"
    assert result["confidence"] > 0.70
    assert result["probabilities"]["Brown"] > result["probabilities"]["Blue"]
    assert result["probabilities"]["Brown"] > result["probabilities"]["Intermediate"]


def test_predict_eye_color_mlr_intermediate():
    """Heterozygous at HERC2 should give mixed/indeterminate prediction."""
    genome = {
        "rs12913832": "AG",  # HERC2 heterozygous
    }
    result = predict_eye_color_mlr(genome)
    assert result["prediction"] == "Mixed/Indeterminate"
    # All three probabilities should be meaningfully non-zero
    assert result["probabilities"]["Blue"] > 0.10
    assert result["probabilities"]["Brown"] > 0.10
    assert result["probabilities"]["Intermediate"] > 0.10


def test_predict_eye_color_contributions():
    """Verify that SNP contributions are tracked."""
    genome = {
        "rs12913832": "GG",
        "rs1800407": "AG",  # OCA2 one A allele
    }
    result = predict_eye_color_mlr(genome)
    assert len(result["contributions"]) >= 1
    rsids = [c["rsid"] for c in result["contributions"]]
    assert "rs12913832" in rsids


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


def test_derive_blood_type_ab():
    """Two functional alleles + GT should give AB."""
    genome = {"rs8176719": "II", "rs8176746": "GT"}
    result = derive_blood_type(genome)
    assert result["blood_type"] == "AB"


def test_derive_blood_type_ambiguous():
    """One O allele + GT should give ambiguous A/B."""
    genome = {"rs8176719": "ID", "rs8176746": "GT"}
    result = derive_blood_type(genome)
    assert "ambiguous" in result["blood_type"].lower() or "A or B" in result["blood_type"]


def test_derive_blood_type_dash_normalization():
    """Dash '-' should be normalized to 'D'."""
    genome = {"rs8176719": "--", "rs8176746": "GG"}
    result = derive_blood_type(genome)
    assert result["blood_type"] == "O"


def test_derive_blood_type_missing_snps():
    """Missing SNPs should return Unknown."""
    assert derive_blood_type({})["blood_type"] == "Unknown"
    assert derive_blood_type({"rs8176719": "DD"})["blood_type"] == "Unknown"


def test_derive_blood_type_unknown_o_genotype():
    """Unrecognized O genotype should return Unknown."""
    genome = {"rs8176719": "XX", "rs8176746": "GG"}
    result = derive_blood_type(genome)
    assert result["blood_type"] == "Unknown"


def test_derive_blood_type_unknown_ab_genotype():
    """Unrecognized A/B genotype should return Unknown."""
    genome = {"rs8176719": "II", "rs8176746": "AA"}
    result = derive_blood_type(genome)
    assert "Unknown" in result["blood_type"]


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


def test_analyze_traits_genome_with_dict_format():
    """Test genome data in dict format (from fast_loader)."""
    mock_traits = {
        "rs123": {
            "gene": "TEST",
            "category": "Eye Color",
            "variants": {"AA": {"status": "blue", "desc": "Blue", "magnitude": 1}},
        }
    }
    genome = {"rs123": {"chromosome": "1", "position": "100", "genotype": "AA"}}
    with patch("analyze_dna.generate_traits_report.TRAITS_SNPS", mock_traits):
        results = analyze_traits_genome(genome)
        assert results["summary"]["analyzed_traits"] == 1


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
    result = generate_traits_report(results, "John")
    assert "Genetic Traits Report for John" in result
    assert "Blue" in result


def test_generate_traits_report_with_categories():
    """Test report with actual category findings."""
    results = {
        "summary": {"total_snps": 100, "analyzed_traits": 3},
        "eye_color_mlr": {
            "prediction": "Brown",
            "confidence": 0.8,
            "probabilities": {"Blue": 0.1, "Intermediate": 0.1, "Brown": 0.8},
            "contributions": [{"rsid": "rs12913832", "genotype": "AA", "effect_allele": "G", "dosage": 0}],
            "reason": "",
        },
        "blood_type": {"blood_type": "A", "o_status": "II", "ab_status": "GG", "reason": "derived"},
        "by_category": {
            "Taste & Smell": [
                {
                    "gene": "TAS2R38",
                    "rsid": "rs713598",
                    "genotype": "CC",
                    "status": "taster",
                    "description": "Bitter taster",
                    "magnitude": 1,
                    "category": "Taste & Smell",
                },
            ],
            "Physical Traits": [
                {
                    "gene": "ABCC11",
                    "rsid": "rs17822931",
                    "genotype": "AA",
                    "status": "dry",
                    "description": "Dry earwax",
                    "magnitude": 1,
                    "category": "Physical Traits",
                },
            ],
        },
        "findings": [
            {
                "gene": "TAS2R38",
                "rsid": "rs713598",
                "genotype": "CC",
                "status": "taster",
                "description": "Bitter taster",
                "magnitude": 1,
                "category": "Taste & Smell",
            },
            {
                "gene": "ABCC11",
                "rsid": "rs17822931",
                "genotype": "AA",
                "status": "dry",
                "description": "Dry earwax",
                "magnitude": 1,
                "category": "Physical Traits",
            },
        ],
        "mc1r_red_hair_score": 0,
    }
    result = generate_traits_report(results, "Jane")
    assert "Taste" in result
    assert "Physical" in result
    assert "Jane" in result


def test_generate_traits_report_red_hair():
    """Test red hair section appears when MC1R score > 0."""
    results = {
        "summary": {"total_snps": 100, "analyzed_traits": 1},
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
        "mc1r_red_hair_score": 3,
    }
    result = generate_traits_report(results, "Test")
    assert "MC1R" in result or "red hair" in result.lower()
