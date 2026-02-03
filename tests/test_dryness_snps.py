import pytest
from pathlib import Path
from scripts.fast_loader import load_genome_fast
from scripts.run_full_analysis import analyze_lifestyle_health


def test_dryness_snps_analysis():
    """
    Test that the new dryness/hydration SNPs are correctly detected and classified.
    This test reads a mock genome file containing specific high-risk and carrier
    genotypes for the newly added Dryness section.
    """
    # Path to the test data
    genome_path = Path(__file__).parent / "data" / "dryness_genome.txt"
    assert genome_path.exists(), "Test genome file missing"

    # Load genome
    genome_by_rsid, _ = load_genome_fast(genome_path)

    # Run analysis (empty PharmGKB as we are focusing on lifestyle/health findings)
    results = analyze_lifestyle_health(genome_by_rsid, {})
    findings = results["findings"]

    # Create a map for easy lookup
    findings_map = {f["rsid"]: f for f in findings}

    # 1. FLG rs61816761 (R501X) - CT (Carrier)
    assert "rs61816761" in findings_map
    f = findings_map["rs61816761"]
    assert f["gene"] == "FLG"
    assert "Dryness/Skin" in f["category"]
    assert f["magnitude"] == 3
    assert f["status"] == "carrier"

    # 2. FLG rs558269137 (2282del4) - DD (Homozygous Affected)
    assert "rs558269137" in findings_map
    f = findings_map["rs558269137"]
    assert f["gene"] == "FLG"
    assert f["magnitude"] == 5
    assert f["status"] == "affected"

    # 3. TRPV1 rs8065080 - AA (High Sensitivity)
    assert "rs8065080" in findings_map
    f = findings_map["rs8065080"]
    assert "Dryness/Sensory" in f["category"]
    assert f["magnitude"] == 2
    assert "High Sensitivity" in f["description"]

    # 4. STAT4 rs7582694 - TT (High Risk)
    assert "rs7582694" in findings_map
    f = findings_map["rs7582694"]
    assert "Dryness/Autoimmune" in f["category"]
    assert f["magnitude"] == 3
    assert f["status"] == "high_risk"

    # 5. IRF5 rs10488631 - CC (High Risk)
    assert "rs10488631" in findings_map
    f = findings_map["rs10488631"]
    assert "Dryness/Autoimmune" in f["category"]
    assert f["magnitude"] == 3
    assert f["status"] == "high_risk"

    # 6. PCGF3 rs1044147 - AG (Risk)
    assert "rs1044147" in findings_map
    f = findings_map["rs1044147"]
    assert "Dryness/Pharmacogenomics" in f["category"]
    assert f["magnitude"] == 1
    assert f["status"] == "risk"

    # 7. MC1R rs1805007 - TT (Red Hair / High Risk)
    assert "rs1805007" in findings_map
    f = findings_map["rs1805007"]
    assert "Dryness/Skin" in f["category"]
    assert f["magnitude"] == 3
    assert f["status"] == "red_hair"

    # 8. MC1R rs1805008 - CT (Carrier)
    assert "rs1805008" in findings_map
    f = findings_map["rs1805008"]
    assert "Dryness/Skin" in f["category"]
    assert f["magnitude"] == 2
    assert f["status"] == "carrier"

    print("All specific dryness SNPs correctly identified and classified.")
