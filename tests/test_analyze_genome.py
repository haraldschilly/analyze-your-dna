from unittest.mock import patch

from scripts.analyze_genome import analyze_genome

MOCK_CURATED_SNPS = {
    "rs123": {
        "gene": "TEST1",
        "category": "Test Category",
        "variants": {
            "AA": {"status": "bad", "desc": "Bad thing", "magnitude": 3},
            "GG": {"status": "good", "desc": "Good thing", "magnitude": 0},
        },
    }
}


def test_analyze_genome_logic(mock_genome_data, mock_clinvar_data, mock_pharmgkb_data):
    with patch("scripts.analyze_genome.CURATED_SNPS", MOCK_CURATED_SNPS):
        results = analyze_genome(mock_genome_data, mock_clinvar_data, mock_pharmgkb_data)

        # Check curated findings
        assert len(results["curated_findings"]) == 1
        finding = results["curated_findings"][0]
        assert finding["rsid"] == "rs123"
        assert finding["status"] == "bad"
        assert finding["magnitude"] == 3

        # Check pharmgkb findings
        assert len(results["pharmgkb_findings"]) == 1
        p_finding = results["pharmgkb_findings"][0]
        assert p_finding["rsid"] == "rs123"
        assert p_finding["annotation"] == "High risk"

        # Check clinvar findings (rs123 is at 1:100 which is in mock_clinvar_data)
        assert len(results["clinvar_findings"]) == 1
        c_finding = results["clinvar_findings"][0]
        assert c_finding["rsid"] == "rs123"
        assert c_finding["significance"] == "pathogenic"


def test_analyze_genome_reverse_complement(mock_clinvar_data, mock_pharmgkb_data):
    # Test that it handles reverse strand genotypes (e.g., TT instead of AA if AA is the defined one)
    # But wait, the code handles it by looking up both.

    # Let's mock a genome with "TT" for rs123 (assuming A <-> T)
    # Actually, let's just use a new rsid to be clear

    # Note: The code does `genotype[::-1]` (reverse) not complement.
    # Wait, `genotype[::-1]` for "TT" is "TT". For "AG" it is "GA".
    # The code says: "Try both orientations ... genotype_rev = genotype[::-1]"
    # It does NOT appear to do strand complement (A<->T, G<->C), just string reverse (AG <-> GA).
    # Let's verify that with a test.

    mock_genome_flip = {"rs888": {"chromosome": "3", "position": "400", "genotype": "GA"}}
    mock_curated_flip = {
        "rs888": {
            "gene": "FLIP",
            "category": "Test",
            "variants": {"AG": {"status": "flip_match", "desc": "Matched flip", "magnitude": 1}},
        }
    }

    with patch("scripts.analyze_genome.CURATED_SNPS", mock_curated_flip):
        results = analyze_genome(mock_genome_flip, {}, {})
        assert len(results["curated_findings"]) == 1
        assert results["curated_findings"][0]["status"] == "flip_match"
