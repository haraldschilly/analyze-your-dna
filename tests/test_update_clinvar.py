import gzip

from analyze_dna.update_clinvar import compute_gold_stars, compute_significance_flags, convert_clinvar


def test_compute_gold_stars():
    assert compute_gold_stars("practice guideline") == 4
    assert compute_gold_stars("reviewed by expert panel") == 3
    assert compute_gold_stars("criteria provided, multiple submitters, no conflicts") == 2
    assert compute_gold_stars("no assertion criteria provided") == 0
    assert compute_gold_stars("unknown status") == 0


def test_compute_significance_flags():
    flags = compute_significance_flags("Pathogenic")
    assert flags["pathogenic"] == 1
    assert flags["likely_pathogenic"] == 0

    flags = compute_significance_flags("Likely pathogenic")
    assert flags["pathogenic"] == 0
    assert flags["likely_pathogenic"] == 1

    flags = compute_significance_flags("Benign")
    assert flags["benign"] == 1


def test_convert_clinvar(tmp_path):
    input_gz = tmp_path / "input.txt.gz"
    output_tsv = tmp_path / "output.tsv"

    content = "Assembly\tPositionVCF\tReferenceAlleleVCF\tAlternateAlleleVCF\tClinicalSignificance\tReviewStatus\tChromosome\tType\tVariationID\tRCVaccession\tSCVsForAggregateGermlineClassification\tAlleleID\tGeneSymbol\tName\tLastEvaluated\tNumberSubmitters\tPhenotypeList\tOrigin\tOtherIDs\n"
    content += "GRCh37\t100\tA\tG\tPathogenic\tPractice guideline\t1\tSNP\t1\tRCV1\tSCV1\t1\tGENE1\tHGVS1\t2026\t1\tTrait1\tgermline\tID1\n"

    with gzip.open(input_gz, "wt") as f:
        f.write(content)

    stats = convert_clinvar(input_gz, output_tsv)
    assert stats["written_rows"] == 1
    assert stats["total_rows"] == 1
    assert output_tsv.exists()

    # Check output content
    with open(output_tsv) as f:
        lines = f.readlines()
        assert len(lines) == 2  # Header + 1 row
        assert "GENE1" in lines[1]
        assert "4" in lines[1]  # gold stars
