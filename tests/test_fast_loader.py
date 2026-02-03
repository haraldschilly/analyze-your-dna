from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import scripts.fast_loader as fast_loader

# =============================================================================
# MOCKED DATA
# =============================================================================

GENOME_CONTENT = """# Comment
rs123	1	100	AA
rs456	1	200	GT
rs789	1	300	--
"""

CLINVAR_CONTENT = "\n".join(
    [
        "\t".join(
            [
                "chrom",
                "pos",
                "symbol",
                "ref",
                "alt",
                "clinical_significance",
                "review_status",
                "gold_stars",
                "all_traits",
                "inheritance_modes",
                "hgvs_c",
                "hgvs_p",
            ]
        ),
        "\t".join(
            [
                "1",
                "100",
                "TEST1",
                "A",
                "G",
                "pathogenic",
                "criteria",
                "1",
                "Disease A",
                "AD",
                "c.100A>G",
                "p.Lys100Glu",
            ]
        ),
        "\t".join(
            [
                "1",
                "200",
                "TEST2",
                "G",
                "A",
                "benign",
                "criteria",
                "1",
                "Disease B",
                "AR",
                "c.200G>A",
                "p.Arg200Gln",
            ]
        ),
    ]
)

# =============================================================================
# MOCKING POLARS
# =============================================================================


class MockExpr:
    def __init__(self, name=""):
        self.name = name

    def cast(self, _):
        return self

    def alias(self, _):
        return self

    def is_in(self, _):
        return self

    def __add__(self, _):
        return self

    def __eq__(self, _):
        return self

    def __ne__(self, _):
        return self

    def __len__(self):
        return 1


class MockPolarsDataFrame:
    def __init__(self, data=None):
        self.data = data or []

    def __len__(self):
        return len(self.data)

    def filter(self, *args, **kwargs):
        # Return self for chaining, simplistic mocking
        return self

    def with_columns(self, *args, **kwargs):
        # Stub
        return self

    def iter_rows(self, named=True):
        return self.data


class MockPolars:
    Utf8 = "Utf8"
    Int64 = "Int64"

    def col(self, name):
        return MockExpr(name)

    def lit(self, val):
        return MockExpr(str(val))

    def read_csv(self, *args, **kwargs):
        # Return data matching our test scenarios
        if "new_columns" in kwargs:  # load_genome uses new_columns
            return MockPolarsDataFrame(
                [
                    {"rsid": "rs123", "chromosome": "1", "position": "100", "genotype": "AA"},
                    {"rsid": "rs456", "chromosome": "1", "position": "200", "genotype": "GT"},
                ]
            )
        else:  # load_clinvar does not
            # Mimic the DataFrame structure for ClinVar
            return MockPolarsDataFrame(
                [
                    {
                        "chrom": 1,
                        "pos": 100,
                        "symbol": "TEST1",
                        "ref": "A",
                        "alt": "G",
                        "clinical_significance": "pathogenic",
                        "review_status": "criteria",
                        "gold_stars": 1,
                        "pos_key": "1:100",  # Simulate the added column
                    },
                    {
                        "chrom": 1,
                        "pos": 200,
                        "symbol": "TEST2",
                        "ref": "G",
                        "alt": "A",
                        "clinical_significance": "benign",
                        "review_status": "criteria",
                        "gold_stars": 1,
                        "pos_key": "1:200",
                    },
                ]
            )


# =============================================================================
# TESTS (STDLIB)
# =============================================================================


def test_load_genome_stdlib():
    """Test loading genome with standard library (csv)."""
    with patch("builtins.open", mock_open(read_data=GENOME_CONTENT)):
        with patch("scripts.fast_loader.USING_POLARS", False):
            genome_by_rsid, genome_by_position = fast_loader._load_genome_stdlib(Path("dummy.txt"))

            assert len(genome_by_rsid) == 2
            assert "rs123" in genome_by_rsid
            assert "rs456" in genome_by_rsid
            assert "rs789" not in genome_by_rsid  # Should be skipped (no call "--")

            assert genome_by_rsid["rs123"]["genotype"] == "AA"
            assert genome_by_position["1:100"]["rsid"] == "rs123"


def test_load_clinvar_stdlib():
    """Test loading ClinVar with standard library (csv)."""
    # User has rs123 at 1:100 with 'AG' (Heterozygous match for 1:100 A->G)
    genome_by_position = {
        "1:100": {"rsid": "rs123", "genotype": "AG"},
        "1:200": {"rsid": "rs456", "genotype": "GG"},  # Reference only match
    }

    with patch("builtins.open", mock_open(read_data=CLINVAR_CONTENT)):
        findings, stats = fast_loader._load_clinvar_stdlib(Path("dummy.txt"), genome_by_position)

        # 1:100 should match (User AG, Alt G)
        # 1:200 should be matched at position-level, but skipped for allele check

        assert stats["matched"] == 2
        assert stats["pathogenic_matched"] == 1
        assert len(findings["pathogenic"]) == 1
        assert findings["pathogenic"][0]["rsid"] == "rs123"


# =============================================================================
# TESTS (POLARS)
# =============================================================================


def test_load_genome_polars():
    """Test loading genome using mocked Polars."""
    mock_pl = MockPolars()

    # Patch 'pl' inside fast_loader module
    with patch("scripts.fast_loader.pl", mock_pl):
        with patch("scripts.fast_loader.USING_POLARS", True):
            genome_by_rsid, genome_by_position = fast_loader._load_genome_polars(Path("dummy.txt"))

            assert len(genome_by_rsid) == 2
            assert "rs123" in genome_by_rsid
            assert genome_by_rsid["rs123"]["genotype"] == "AA"
            assert genome_by_position["1:100"]["rsid"] == "rs123"


def test_load_clinvar_polars():
    """Test loading ClinVar using mocked Polars."""
    # User has 1:100 (AG) -> Matches Pathogenic A->G
    genome_by_position = {
        "1:100": {"rsid": "rs123", "genotype": "AG"},
    }

    # Create tailored mock dataframe
    filtered_df = MockPolarsDataFrame(
        [
            {
                "chrom": 1,
                "pos": 100,
                "symbol": "TEST1",
                "ref": "A",
                "alt": "G",
                "clinical_significance": "pathogenic",
                "review_status": "criteria",
                "gold_stars": 1,
                "pos_key": "1:100",
            }
        ]
    )

    mock_pl = MockPolars()

    # The code calls read_csv().with_columns().filter()
    # Let's refine the mock structure
    mock_chain = MagicMock()
    mock_chain.__len__.return_value = 1
    mock_chain.with_columns.return_value = mock_chain
    mock_chain.filter.return_value = filtered_df  # The final result of the chain

    mock_pl.read_csv = MagicMock(return_value=mock_chain)

    with patch("scripts.fast_loader.pl", mock_pl):
        with patch("scripts.fast_loader.USING_POLARS", True):
            findings, stats = fast_loader._load_clinvar_polars(Path("dummy.txt"), genome_by_position)

            assert len(findings["pathogenic"]) == 1
            assert findings["pathogenic"][0]["rsid"] == "rs123"
            assert stats["pathogenic_matched"] == 1


def test_switch_logic():
    """Test that the top-level functions use proper logic to switch."""
    with patch("scripts.fast_loader.USING_POLARS", False):
        with patch("scripts.fast_loader._load_genome_stdlib") as mock_std:
            fast_loader.load_genome_fast(Path("x"))
            mock_std.assert_called_once()

    with patch("scripts.fast_loader.USING_POLARS", True):
        with patch("scripts.fast_loader.pl", MockPolars()):  # satisfy assert pl is not None
            with patch("scripts.fast_loader._load_genome_polars") as mock_pl:
                fast_loader.load_genome_fast(Path("x"))
                mock_pl.assert_called_once()
