from analyze_dna.generate_exhaustive_report import (
    format_evidence_level,
    format_magnitude,
    generate_executive_summary,
    generate_finding_section,
    generate_full_findings,
    generate_pharmgkb_section,
    generate_priority_findings,
    get_clinical_context,
    get_related_pathways,
)


def test_get_clinical_context():
    assert get_clinical_context("MTHFR", "significantly_reduced") is not None
    assert get_clinical_context("NonExistent", "None") is None


def test_get_related_pathways():
    assert "Methylation Cycle" in get_related_pathways("MTHFR")
    assert get_related_pathways("NonExistent") == []


def test_format_magnitude():
    assert "HIGH" in format_magnitude(3)
    assert "MODERATE" in format_magnitude(2)
    assert "LOW" in format_magnitude(1)
    assert "NEUTRAL" in format_magnitude(0)


def test_format_evidence_level():
    assert "1A" in format_evidence_level("1A")
    assert "2A" in format_evidence_level("2A")
    assert "X" in format_evidence_level("X")


def test_generate_finding_section():
    finding = {
        "gene": "MTHFR",
        "rsid": "rs1",
        "category": "Methylation",
        "genotype": "AA",
        "status": "significantly_reduced",
        "description": "Desc",
        "magnitude": 3,
        "note": "Note",
    }
    result = generate_finding_section(finding, 1)
    assert "MTHFR" in result
    assert "Mechanism" in result
    assert "Recommended Actions" in result


def test_generate_pharmgkb_section():
    finding = {
        "gene": "CYP2C19",
        "rsid": "rs1",
        "drugs": "DrugA",
        "genotype": "AA",
        "annotation": "Ann",
        "level": "1A",
        "category": "Cat",
    }
    result = generate_pharmgkb_section(finding, 1)
    assert "CYP2C19" in result
    assert "clinical guideline" in result


def test_summaries():
    data = {
        "summary": {"total_snps": 100},
        "findings": [{"gene": "MTHFR", "magnitude": 3, "category": "Methylation", "status": "significantly_reduced"}],
        "pharmgkb_findings": [{"gene": "CYP2C19", "level": "1A", "category": "Drug Metabolism"}],
    }
    exec_summary = generate_executive_summary(data)
    assert "Methylation" in exec_summary
    assert "High Impact (magnitude ≥3):** 1" in exec_summary

    priority = generate_priority_findings(data["findings"])
    assert "Priority Findings" in priority
    assert "MTHFR" in priority

    full = generate_full_findings(data["findings"])
    assert "Methylation" in full
    assert "MTHFR" in full
