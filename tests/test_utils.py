import gzip
from pathlib import Path
from unittest.mock import mock_open, patch

from analyze_dna.utils import (
    ensure_clinvar,
    load_genome,
    load_pharmgkb,
    sanitize_markdown,
    snp_database_stats,
)


def test_sanitize_markdown():
    """Test the Markdown sanitization utility."""
    assert sanitize_markdown(None) == ""
    assert sanitize_markdown("") == ""

    # Test HTML escaping
    assert sanitize_markdown("<script>alert(1)</script>") == r"&lt;script&gt;alert\(1\)&lt;/script&gt;"

    # Test Markdown escaping
    assert sanitize_markdown("# Header") == r"\# Header"
    assert sanitize_markdown("**Bold**") == r"\*\*Bold\*\*"
    assert sanitize_markdown("[Link](url)") == r"\[Link\]\(url\)"
    assert sanitize_markdown("`Code`") == r"\`Code\`"

    # Test combination
    assert sanitize_markdown("** <script>") == r"\*\* &lt;script&gt;"


def test_load_genome():
    content = "# Comment\nrs123\t1\t100\tAA\nrs456\t1\t200\tGT\nrs789\t1\t300\t--\n"
    with patch("builtins.open", mock_open(read_data=content)):
        genome = load_genome(Path("dummy.txt"))
        assert len(genome) == 2
        assert genome["rs123"] == {"chromosome": "1", "position": "100", "genotype": "AA"}
        assert "rs789" not in genome  # skipped no-call


def test_load_pharmgkb():
    ann_content = "Clinical Annotation ID\tVariant/Haplotypes\tGene\tDrug(s)\tPhenotype(s)\tLevel of Evidence\tPhenotype Category\n1\trs123\tGENE1\tDrugA\tPhenoA\t1A\tTox\n"
    allele_content = "Clinical Annotation ID\tGenotype/Allele\tAnnotation Text\n1\tAA\tHigh risk\n"

    # We need to handle multiple open calls for different files
    def multi_mock_open(*args, **kwargs):
        path = str(args[0])
        if "ann" in path:
            return mock_open(read_data=ann_content).return_value
        return mock_open(read_data=allele_content).return_value

    with patch("builtins.open", side_effect=multi_mock_open):
        pharmgkb = load_pharmgkb(Path("ann.tsv"), Path("allele.tsv"))
        assert "rs123" in pharmgkb
        assert pharmgkb["rs123"]["gene"] == "GENE1"
        assert pharmgkb["rs123"]["genotypes"]["AA"] == "High risk"


def test_ensure_clinvar(tmp_path):
    # Test decompression
    gz_path = tmp_path / "clinvar_alleles.tsv.gz"
    tsv_path = tmp_path / "clinvar_alleles.tsv"

    with gzip.open(gz_path, "wb") as f:
        f.write(b"test content")

    result_path = ensure_clinvar(tmp_path)
    assert result_path == str(tsv_path)
    assert tsv_path.exists()
    assert tsv_path.read_text() == "test content"

    # Test when tsv already exists
    with patch("gzip.open") as mock_gz:
        ensure_clinvar(tmp_path)
        mock_gz.assert_not_called()


def test_snp_database_stats(capsys):
    # Mock the databases to keep output small
    mock_db = {"rs123": {"category": "Cat1", "gene": "Gene1"}}
    with patch("analyze_dna.comprehensive_snp_database.COMPREHENSIVE_SNPS", mock_db):
        with patch("analyze_dna.analyze_genome.CURATED_SNPS", mock_db):
            with patch("analyze_dna.traits_snp_database.TRAITS_SNPS", mock_db):
                snp_database_stats()
                captured = capsys.readouterr()
                assert "=== COMPREHENSIVE_SNPS" in captured.out
                assert "| Cat1 | 1 | 1 | Gene1 |" in captured.out
