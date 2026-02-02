import pytest
import sys
from pathlib import Path

# Add scripts directory to sys.path to allow imports from scripts
sys.path.append(str(Path(__file__).parents[1] / "scripts"))

@pytest.fixture
def mock_genome_data():
    return {
        "rs123": {"chromosome": "1", "position": "100", "genotype": "AA"},
        "rs456": {"chromosome": "1", "position": "200", "genotype": "GT"},
    }

@pytest.fixture
def mock_genome_by_position():
    return {
        "1:100": {"rsid": "rs123", "genotype": "AA"},
        "1:200": {"rsid": "rs456", "genotype": "GT"},
    }

@pytest.fixture
def mock_clinvar_data():
    return {
        "chr1:100": {
            "gene": "TEST1",
            "significance": "pathogenic",
            "traits": "Disease A",
            "review_status": "criteria provided",
            "gold_stars": "2"
        }
    }

@pytest.fixture
def mock_pharmgkb_data():
    return {
        "rs123": {
            "gene": "TEST1",
            "drugs": "Drug A",
            "level": "1A",
            "category": "Toxicity",
            "genotypes": {
                "AA": "High risk",
                "GG": "Normal"
            }
        }
    }
