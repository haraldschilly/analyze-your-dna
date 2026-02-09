import io
from pathlib import Path
from unittest.mock import mock_open, patch

from analyze_dna.full_health_analysis import (
    analyze_genome,
    generate_comprehensive_report,
    write_action_plan,
    write_category_interpretation,
)


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

    result = generate_comprehensive_report(results)
    assert "Complete Genetic Health Optimization Report" in result
    assert "Methylation" in result
    assert "DrugA" in result


def test_generate_report_no_high_impact():
    """Test report generation when no high-impact findings exist."""
    results = {
        "summary": {
            "total_snps": 1000,
            "analyzed_snps": 5,
            "high_impact": 0,
            "moderate_impact": 1,
            "low_impact": 2,
        },
        "findings": [
            {
                "gene": "GENE1",
                "rsid": "rs1",
                "category": "Methylation",
                "genotype": "AG",
                "status": "carrier",
                "magnitude": 1,
                "description": "Minor finding",
                "note": "",
            }
        ],
        "by_category": {
            "Methylation": [
                {
                    "gene": "GENE1",
                    "rsid": "rs1",
                    "category": "Methylation",
                    "genotype": "AG",
                    "status": "carrier",
                    "magnitude": 1,
                    "description": "Minor finding",
                    "note": "",
                }
            ]
        },
        "pharmgkb_findings": [],
    }

    result = generate_comprehensive_report(results)
    assert "No high-impact" in result


# =============================================================================
# write_category_interpretation tests
# =============================================================================


def _interpret(category, findings_list):
    """Helper: run write_category_interpretation and return output."""
    f = io.StringIO()
    write_category_interpretation(f, category, findings_list)
    return f.getvalue()


def test_interpretation_methylation_mthfr():
    findings = [
        {
            "gene": "MTHFR",
            "status": "affected",
            "magnitude": 3,
            "rsid": "rs1801133",
            "genotype": "TT",
            "description": "Reduced enzyme",
            "note": "",
            "category": "Methylation",
        },
    ]
    result = _interpret("Methylation", findings)
    assert "methylfolate" in result.lower()
    assert "homocysteine" in result.lower()


def test_interpretation_methylation_mthfr_with_slow_comt():
    findings = [
        {
            "gene": "MTHFR",
            "status": "affected",
            "magnitude": 3,
            "rsid": "rs1801133",
            "genotype": "TT",
            "description": "Reduced",
            "note": "",
            "category": "Methylation",
        },
        {
            "gene": "COMT",
            "status": "slow",
            "magnitude": 2,
            "rsid": "rs4680",
            "genotype": "AA",
            "description": "Slow",
            "note": "",
            "category": "Methylation",
        },
    ]
    result = _interpret("Methylation", findings)
    assert "COMT" in result
    assert "anxiety" in result.lower() or "overstimulation" in result.lower()


def test_interpretation_neurotransmitters_slow_comt():
    findings = [
        {
            "gene": "COMT",
            "status": "slow",
            "magnitude": 2,
            "rsid": "rs4680",
            "genotype": "AA",
            "description": "Slow",
            "note": "",
            "category": "Neurotransmitters",
        },
    ]
    result = _interpret("Neurotransmitters", findings)
    assert "Slow COMT" in result
    assert "working memory" in result.lower()
    assert "stress" in result.lower()


def test_interpretation_neurotransmitters_fast_comt():
    findings = [
        {
            "gene": "COMT",
            "status": "fast",
            "magnitude": 1,
            "rsid": "rs4680",
            "genotype": "GG",
            "description": "Fast",
            "note": "",
            "category": "Neurotransmitters",
        },
    ]
    result = _interpret("Neurotransmitters", findings)
    assert "Fast COMT" in result
    assert "stress resilience" in result.lower()


def test_interpretation_neurotransmitters_bdnf():
    findings = [
        {
            "gene": "BDNF",
            "status": "reduced",
            "magnitude": 2,
            "rsid": "rs6265",
            "genotype": "CT",
            "description": "Reduced BDNF",
            "note": "",
            "category": "Neurotransmitters",
        },
    ]
    result = _interpret("Neurotransmitters", findings)
    assert "BDNF" in result
    assert "exercise" in result.lower()


def test_interpretation_fitness_power():
    findings = [
        {
            "gene": "ACTN3",
            "status": "power",
            "magnitude": 1,
            "rsid": "rs1815739",
            "genotype": "CC",
            "description": "Power",
            "note": "",
            "category": "Fitness",
        },
    ]
    result = _interpret("Fitness", findings)
    assert "power" in result.lower()
    assert "Sprinting" in result or "sprinting" in result.lower()


def test_interpretation_fitness_endurance():
    findings = [
        {
            "gene": "ACTN3",
            "status": "endurance",
            "magnitude": 1,
            "rsid": "rs1815739",
            "genotype": "TT",
            "description": "Endurance",
            "note": "",
            "category": "Fitness",
        },
        {
            "gene": "ACE",
            "status": "endurance",
            "magnitude": 1,
            "rsid": "rs1799752",
            "genotype": "II",
            "description": "Endurance ACE",
            "note": "",
            "category": "Fitness",
        },
    ]
    result = _interpret("Fitness", findings)
    assert "endurance" in result.lower()
    assert "altitude" in result.lower() or "oxygen" in result.lower()


def test_interpretation_nutrition_fto():
    findings = [
        {
            "gene": "FTO",
            "status": "elevated",
            "magnitude": 2,
            "rsid": "rs9939609",
            "genotype": "AA",
            "description": "Elevated obesity risk",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _interpret("Nutrition", findings)
    assert "appetite" in result.lower() or "satiety" in result.lower()


def test_interpretation_nutrition_vitamin_d():
    findings = [
        {
            "gene": "GC",
            "status": "low",
            "magnitude": 2,
            "rsid": "rs2282679",
            "genotype": "CC",
            "description": "Low vitamin D",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _interpret("Nutrition", findings)
    assert "vitamin D" in result or "Vitamin D" in result
    assert "2,000" in result or "5,000" in result


def test_interpretation_nutrition_fads1():
    findings = [
        {
            "gene": "FADS1",
            "status": "low_conversion",
            "magnitude": 2,
            "rsid": "rs174547",
            "genotype": "TT",
            "description": "Low conversion",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _interpret("Nutrition", findings)
    assert "omega-3" in result.lower() or "EPA" in result


def test_interpretation_nutrition_lactose():
    findings = [
        {
            "gene": "MCM6/LCT",
            "status": "lactose_intolerant",
            "magnitude": 2,
            "rsid": "rs4988235",
            "genotype": "CC",
            "description": "Lactose intolerant",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _interpret("Nutrition", findings)
    assert "lactose" in result.lower() or "Lactose" in result


def test_interpretation_cardiovascular_bp():
    findings = [
        {
            "gene": "AGTR1",
            "status": "risk",
            "magnitude": 2,
            "rsid": "rs5186",
            "genotype": "CC",
            "description": "BP risk",
            "note": "",
            "category": "Cardiovascular",
        },
        {
            "gene": "AGT",
            "status": "risk",
            "magnitude": 2,
            "rsid": "rs699",
            "genotype": "TT",
            "description": "BP risk",
            "note": "",
            "category": "Cardiovascular",
        },
    ]
    result = _interpret("Cardiovascular", findings)
    assert "blood pressure" in result.lower() or "Blood Pressure" in result


def test_interpretation_cardiovascular_clotting():
    findings = [
        {
            "gene": "F5",
            "status": "carrier",
            "magnitude": 4,
            "rsid": "rs6025",
            "genotype": "GA",
            "description": "Factor V Leiden carrier",
            "note": "",
            "category": "Cardiovascular",
        },
    ]
    result = _interpret("Cardiovascular", findings)
    assert "clot" in result.lower()
    assert "estrogen" in result.lower() or "flight" in result.lower()


def test_interpretation_caffeine_slow_and_anxious():
    findings = [
        {
            "gene": "CYP1A2",
            "status": "slow",
            "magnitude": 2,
            "rsid": "rs762551",
            "genotype": "AC",
            "description": "Slow metabolizer",
            "note": "",
            "category": "Caffeine Response",
        },
        {
            "gene": "ADORA2A",
            "status": "anxiety_prone",
            "magnitude": 1,
            "rsid": "rs5751876",
            "genotype": "TT",
            "description": "Anxiety-prone",
            "note": "",
            "category": "Caffeine Response",
        },
    ]
    result = _interpret("Caffeine Response", findings)
    assert "slower metabolizer" in result.lower() or "anxiety" in result.lower()
    assert "L-theanine" in result or "l-theanine" in result.lower()


def test_interpretation_caffeine_slow_only():
    findings = [
        {
            "gene": "CYP1A2",
            "status": "slow",
            "magnitude": 2,
            "rsid": "rs762551",
            "genotype": "AC",
            "description": "Slow metabolizer",
            "note": "",
            "category": "Caffeine Response",
        },
    ]
    result = _interpret("Caffeine Response", findings)
    assert "morning" in result.lower() or "noon" in result.lower()


def test_interpretation_caffeine_anxiety_only():
    findings = [
        {
            "gene": "ADORA2A",
            "status": "anxiety_prone",
            "magnitude": 1,
            "rsid": "rs5751876",
            "genotype": "TT",
            "description": "Anxiety-prone",
            "note": "",
            "category": "Caffeine Response",
        },
    ]
    result = _interpret("Caffeine Response", findings)
    assert "lower doses" in result.lower() or "L-theanine" in result


def test_interpretation_caffeine_favorable():
    findings = [
        {
            "gene": "CYP1A2",
            "status": "fast",
            "magnitude": 0,
            "rsid": "rs762551",
            "genotype": "AA",
            "description": "Fast metabolizer",
            "note": "",
            "category": "Caffeine Response",
        },
    ]
    result = _interpret("Caffeine Response", findings)
    assert "favorable" in result.lower()


# =============================================================================
# write_action_plan tests
# =============================================================================


def _action_plan(findings_list):
    """Helper: run write_action_plan and return output."""
    results = {"findings": findings_list}
    f = io.StringIO()
    write_action_plan(f, results)
    return f.getvalue()


def test_action_plan_mthfr():
    findings = [
        {
            "gene": "MTHFR",
            "magnitude": 3,
            "status": "affected",
            "rsid": "rs1801133",
            "genotype": "TT",
            "description": "Reduced",
            "note": "",
            "category": "Methylation",
        },
    ]
    result = _action_plan(findings)
    assert "methylfolate" in result.lower()
    assert "homocysteine" in result.lower()


def test_action_plan_comt_slow():
    findings = [
        {
            "gene": "COMT",
            "magnitude": 2,
            "status": "slow",
            "rsid": "rs4680",
            "genotype": "AA",
            "description": "Slow COMT",
            "note": "",
            "category": "Neurotransmitters",
        },
    ]
    result = _action_plan(findings)
    assert "Stress Management" in result or "stress" in result.lower()
    assert "Magnesium" in result or "magnesium" in result


def test_action_plan_vitamin_d():
    findings = [
        {
            "gene": "GC",
            "magnitude": 2,
            "status": "low",
            "rsid": "rs2282679",
            "genotype": "CC",
            "description": "Low",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _action_plan(findings)
    assert "Vitamin D" in result
    assert "IU" in result


def test_action_plan_fads1():
    findings = [
        {
            "gene": "FADS1",
            "magnitude": 2,
            "status": "low_conversion",
            "rsid": "rs174547",
            "genotype": "TT",
            "description": "Low conversion",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _action_plan(findings)
    assert "Omega-3" in result or "omega-3" in result
    assert "fish" in result.lower() or "algae" in result.lower()


def test_action_plan_fto():
    findings = [
        {
            "gene": "FTO",
            "magnitude": 2,
            "status": "elevated",
            "rsid": "rs9939609",
            "genotype": "AA",
            "description": "Elevated",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _action_plan(findings)
    assert "protein" in result.lower() or "Satiety" in result


def test_action_plan_tcf7l2():
    findings = [
        {
            "gene": "TCF7L2",
            "magnitude": 3,
            "status": "risk",
            "rsid": "rs7903146",
            "genotype": "TT",
            "description": "Diabetes risk",
            "note": "",
            "category": "Nutrition",
        },
    ]
    result = _action_plan(findings)
    assert "Carb" in result or "glycemic" in result.lower()


def test_action_plan_bp_genes():
    findings = [
        {
            "gene": "AGTR1",
            "magnitude": 2,
            "status": "risk",
            "rsid": "rs5186",
            "genotype": "CC",
            "description": "BP risk",
            "note": "",
            "category": "Cardiovascular",
        },
    ]
    result = _action_plan(findings)
    assert "Blood Pressure" in result or "DASH" in result


def test_action_plan_hfe():
    findings = [
        {
            "gene": "HFE",
            "magnitude": 2,
            "status": "carrier",
            "rsid": "rs1800562",
            "genotype": "GA",
            "description": "Carrier",
            "note": "",
            "category": "Iron Metabolism",
        },
    ]
    result = _action_plan(findings)
    assert "iron" in result.lower() or "ferritin" in result.lower()


def test_action_plan_bdnf():
    findings = [
        {
            "gene": "BDNF",
            "magnitude": 2,
            "status": "reduced",
            "rsid": "rs6265",
            "genotype": "CT",
            "description": "Reduced",
            "note": "",
            "category": "Neurotransmitters",
        },
    ]
    result = _action_plan(findings)
    assert "BDNF" in result
    assert "exercise" in result.lower()


def test_action_plan_actn3_endurance():
    findings = [
        {
            "gene": "ACTN3",
            "magnitude": 1,
            "status": "endurance",
            "rsid": "rs1815739",
            "genotype": "TT",
            "description": "Endurance",
            "note": "",
            "category": "Fitness",
        },
    ]
    result = _action_plan(findings)
    assert "endurance" in result.lower()


def test_action_plan_actn3_power():
    findings = [
        {
            "gene": "ACTN3",
            "magnitude": 1,
            "status": "power",
            "rsid": "rs1815739",
            "genotype": "CC",
            "description": "Power",
            "note": "",
            "category": "Fitness",
        },
    ]
    result = _action_plan(findings)
    assert "power" in result.lower() or "strength" in result.lower()


def test_action_plan_empty():
    """When no actionable findings, should still produce valid plan with defaults."""
    result = _action_plan([])
    assert "Immediate Actions" in result
    assert "Dietary Recommendations" in result
    assert "No urgent actions required" in result
