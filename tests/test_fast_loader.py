import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
from scripts.fast_loader import load_genome_fast, _load_genome_stdlib

GENOME_CONTENT = """# Comment
rs123	1	100	AA
rs456	1	200	GT
rs789	1	300	--
"""

def test_load_genome_stdlib():
    with patch("builtins.open", mock_open(read_data=GENOME_CONTENT)):
        genome_by_rsid, genome_by_position = _load_genome_stdlib(Path("dummy.txt"))
        
        assert len(genome_by_rsid) == 2
        assert "rs123" in genome_by_rsid
        assert "rs456" in genome_by_rsid
        assert "rs789" not in genome_by_rsid  # Should be skipped (no call) 
        
        assert genome_by_rsid["rs123"]["genotype"] == "AA"
        assert genome_by_position["1:100"]["rsid"] == "rs123"

@patch("scripts.fast_loader.USING_POLARS", False)
def test_load_genome_fast_fallback():
    # Forces standard lib path even if polars is installed
    with patch("builtins.open", mock_open(read_data=GENOME_CONTENT)):
        genome_by_rsid, _ = load_genome_fast(Path("dummy.txt"))
        assert len(genome_by_rsid) == 2
